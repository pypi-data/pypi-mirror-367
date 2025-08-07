"""
Main static analyzer for yaapp code quality rules.
"""

import ast
import os
import fnmatch
from pathlib import Path
from typing import List, Iterator, Optional

from .config import AnalysisConfig, DEFAULT_CONFIG
from .rules import RuleViolation, TryExceptRule
from .reporter import ViolationReporter


class YaappStaticAnalyzer:
    """Main static analyzer for yaapp code."""
    
    def __init__(self, config: AnalysisConfig = None):
        """Initialize analyzer with configuration."""
        self.config = config or DEFAULT_CONFIG
        self.try_except_rule = TryExceptRule(
            allowed_foreign_libs=self.config.allowed_foreign_libraries,
            internal_modules=self.config.internal_modules,
            allowed_exceptions=self.config.allowed_exceptions
        )
        self.reporter = ViolationReporter()
    
    def analyze_file(self, file_path: str) -> List[RuleViolation]:
        """Analyze a single Python file for violations."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
                source_lines = source_code.splitlines()
            
            # Parse the AST
            tree = ast.parse(source_code, filename=file_path)
            
            # Visit all nodes and check for violations
            visitor = TryExceptVisitor(
                file_path=file_path,
                source_lines=source_lines,
                try_except_rule=self.try_except_rule
            )
            visitor.visit(tree)
            violations.extend(visitor.violations)
            
        except SyntaxError as e:
            violations.append(RuleViolation(
                file_path=file_path,
                line_number=e.lineno or 0,
                column_number=e.offset or 0,
                violation_type="syntax_error",
                message=f"Syntax error: {e.msg}",
                suggestion="Fix syntax error before analysis"
            ))
        except Exception as e:
            violations.append(RuleViolation(
                file_path=file_path,
                line_number=0,
                column_number=0,
                violation_type="analysis_error",
                message=f"Analysis error: {str(e)}",
                suggestion="Check file for parsing issues"
            ))
        
        return violations
    
    def analyze_directory(self, directory: str, recursive: bool = True) -> List[RuleViolation]:
        """Analyze all Python files in a directory."""
        violations = []
        
        for file_path in self._find_python_files(directory, recursive):
            if not self._should_exclude_file(file_path):
                file_violations = self.analyze_file(file_path)
                violations.extend(file_violations)
        
        return violations
    
    def analyze_project(self, project_root: str = ".") -> List[RuleViolation]:
        """Analyze the entire yaapp project."""
        violations = []
        
        # Analyze source code
        src_dir = os.path.join(project_root, "src")
        if os.path.exists(src_dir):
            violations.extend(self.analyze_directory(src_dir))
        
        # Analyze examples (with relaxed rules)
        examples_dir = os.path.join(project_root, "examples")
        if os.path.exists(examples_dir):
            # TODO: Use relaxed config for examples
            violations.extend(self.analyze_directory(examples_dir))
        
        return violations
    
    def _find_python_files(self, directory: str, recursive: bool = True) -> Iterator[str]:
        """Find all Python files in directory."""
        directory_path = Path(directory)
        
        if recursive:
            pattern = "**/*.py"
        else:
            pattern = "*.py"
        
        for file_path in directory_path.glob(pattern):
            if file_path.is_file():
                yield str(file_path)
    
    def _should_exclude_file(self, file_path: str) -> bool:
        """Check if file should be excluded from analysis."""
        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False


class TryExceptVisitor(ast.NodeVisitor):
    """AST visitor that finds and analyzes try/except blocks."""
    
    def __init__(self, file_path: str, source_lines: List[str], try_except_rule: TryExceptRule):
        self.file_path = file_path
        self.source_lines = source_lines
        self.try_except_rule = try_except_rule
        self.violations: List[RuleViolation] = []
    
    def visit_Try(self, node: ast.Try):
        """Visit try/except blocks."""
        violations = self.try_except_rule.analyze_try_except(
            node, self.file_path, self.source_lines
        )
        self.violations.extend(violations)
        
        # Continue visiting child nodes
        self.generic_visit(node)
    
    def visit_Raise(self, node: ast.Raise):
        """Visit raise statements (for future rules)."""
        # TODO: Add rules for raise statements if needed
        self.generic_visit(node)


def analyze_files(file_paths: List[str], config: AnalysisConfig = None) -> List[RuleViolation]:
    """Convenience function to analyze multiple files."""
    analyzer = YaappStaticAnalyzer(config)
    violations = []
    
    for file_path in file_paths:
        violations.extend(analyzer.analyze_file(file_path))
    
    return violations


def analyze_project(project_root: str = ".", config: AnalysisConfig = None) -> List[RuleViolation]:
    """Convenience function to analyze entire project."""
    analyzer = YaappStaticAnalyzer(config)
    return analyzer.analyze_project(project_root)