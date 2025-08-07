"""
Static analysis rules for yaapp code quality.
"""

import ast
from typing import List, Set, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ViolationType(Enum):
    """Types of rule violations."""
    FORBIDDEN_TRY_EXCEPT = "forbidden_try_except"
    BARE_EXCEPT = "bare_except"
    BROAD_EXCEPT = "broad_except"
    MISSING_SPECIFIC_EXCEPTION = "missing_specific_exception"
    INTERNAL_CODE_IN_TRY = "internal_code_in_try"


@dataclass
class RuleViolation:
    """Represents a rule violation found during analysis."""
    file_path: str
    line_number: int
    column_number: int
    violation_type: ViolationType
    message: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None


class TryExceptRule:
    """Rule for analyzing try/except blocks."""
    
    def __init__(self, allowed_foreign_libs: Set[str], internal_modules: Set[str], 
                 allowed_exceptions: Set[str]):
        self.allowed_foreign_libs = allowed_foreign_libs
        self.internal_modules = internal_modules
        self.allowed_exceptions = allowed_exceptions
    
    def analyze_try_except(self, node: ast.Try, file_path: str, 
                          source_lines: List[str]) -> List[RuleViolation]:
        """Analyze a try/except block for violations."""
        violations = []
        
        # Check for bare except clauses
        for handler in node.handlers:
            if handler.type is None:
                violations.append(RuleViolation(
                    file_path=file_path,
                    line_number=handler.lineno,
                    column_number=handler.col_offset,
                    violation_type=ViolationType.BARE_EXCEPT,
                    message="Bare except clause found - specify specific exception types",
                    suggestion="Use 'except SpecificException:' instead of 'except:'",
                    code_snippet=self._get_code_snippet(source_lines, handler.lineno)
                ))
        
        # Check for overly broad exception handling
        for handler in node.handlers:
            if (handler.type and 
                isinstance(handler.type, ast.Name) and 
                handler.type.id == 'Exception'):
                violations.append(RuleViolation(
                    file_path=file_path,
                    line_number=handler.lineno,
                    column_number=handler.col_offset,
                    violation_type=ViolationType.BROAD_EXCEPT,
                    message="Overly broad 'except Exception:' found",
                    suggestion="Use specific exception types instead of 'Exception'",
                    code_snippet=self._get_code_snippet(source_lines, handler.lineno)
                ))
        
        # Analyze what's inside the try block
        try_block_calls = self._extract_calls_from_try_block(node.body)
        
        # Check if try block contains only internal yaapp code
        if self._contains_only_internal_code(try_block_calls):
            violations.append(RuleViolation(
                file_path=file_path,
                line_number=node.lineno,
                column_number=node.col_offset,
                violation_type=ViolationType.INTERNAL_CODE_IN_TRY,
                message="try/except around internal yaapp code is forbidden",
                suggestion="Remove try/except or ensure it protects foreign library calls",
                code_snippet=self._get_code_snippet(source_lines, node.lineno, node.end_lineno)
            ))
        
        # Check if exceptions are appropriately specific
        foreign_calls = self._get_foreign_library_calls(try_block_calls)
        if foreign_calls and not self._has_appropriate_exception_handling(node.handlers, foreign_calls):
            violations.append(RuleViolation(
                file_path=file_path,
                line_number=node.lineno,
                column_number=node.col_offset,
                violation_type=ViolationType.MISSING_SPECIFIC_EXCEPTION,
                message="Foreign library calls should have specific exception handling",
                suggestion=f"Add specific exception handling for {', '.join(foreign_calls)}",
                code_snippet=self._get_code_snippet(source_lines, node.lineno, node.end_lineno)
            ))
        
        return violations
    
    def _extract_calls_from_try_block(self, try_body: List[ast.stmt]) -> List[str]:
        """Extract all function/method calls from try block."""
        calls = []
        
        class CallExtractor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    # Handle module.function calls
                    if isinstance(node.func.value, ast.Name):
                        calls.append(f"{node.func.value.id}.{node.func.attr}")
                    else:
                        calls.append(node.func.attr)
                self.generic_visit(node)
        
        for stmt in try_body:
            CallExtractor().visit(stmt)
        
        return calls
    
    def _contains_only_internal_code(self, calls: List[str]) -> bool:
        """Check if calls are only to internal yaapp code."""
        if not calls:
            return False
        
        for call in calls:
            # Check if call is to a foreign library
            if any(call.startswith(lib) for lib in self.allowed_foreign_libs):
                return False
            
            # Check if call is to an internal module
            if any(call.startswith(module) for module in self.internal_modules):
                continue
            
            # If we can't classify it, assume it might be foreign
            return False
        
        return True
    
    def _get_foreign_library_calls(self, calls: List[str]) -> List[str]:
        """Get calls that are to foreign libraries."""
        foreign_calls = []
        
        for call in calls:
            if any(call.startswith(lib) for lib in self.allowed_foreign_libs):
                foreign_calls.append(call)
        
        return foreign_calls
    
    def _has_appropriate_exception_handling(self, handlers: List[ast.ExceptHandler], 
                                          foreign_calls: List[str]) -> bool:
        """Check if exception handling is appropriate for foreign calls."""
        if not handlers:
            return False
        
        # Check if any handler catches appropriate exceptions
        for handler in handlers:
            if handler.type is None:  # Bare except
                return False
            
            if isinstance(handler.type, ast.Name):
                exception_name = handler.type.id
                if exception_name in self.allowed_exceptions:
                    return True
                
                # Check for library-specific exceptions
                for call in foreign_calls:
                    if call.startswith('requests') and 'Request' in exception_name:
                        return True
                    if call.startswith('json') and 'JSON' in exception_name:
                        return True
                    # Add more library-specific checks as needed
        
        return False
    
    def _get_code_snippet(self, source_lines: List[str], start_line: int, 
                         end_line: int = None) -> str:
        """Get code snippet for violation context."""
        if not source_lines:
            return ""
        
        start_idx = max(0, start_line - 1)
        end_idx = min(len(source_lines), (end_line or start_line))
        
        return '\n'.join(source_lines[start_idx:end_idx])