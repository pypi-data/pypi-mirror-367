"""
Tests for the static analysis tool itself.
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from static_analysis import YaappStaticAnalyzer, AnalysisConfig, ViolationReporter
from static_analysis.rules import ViolationType


class TestStaticAnalyzer:
    """Test the static analyzer functionality."""
    
    def test_analyzer_creation(self):
        """Test that analyzer can be created."""
        analyzer = YaappStaticAnalyzer()
        assert analyzer is not None
        assert analyzer.config is not None
    
    def test_forbidden_try_except_detection(self):
        """Test detection of forbidden try/except around internal code."""
        code = '''
import yaapp

def bad_function():
    try:
        yaapp.expose(some_function)  # Internal yaapp code
        return "success"
    except Exception:
        return "error"
'''
        
        violations = self._analyze_code(code)
        
        # Should detect forbidden try/except around internal code
        internal_violations = [
            v for v in violations 
            if v.violation_type == ViolationType.INTERNAL_CODE_IN_TRY
        ]
        assert len(internal_violations) > 0
    
    def test_allowed_try_except_detection(self):
        """Test that try/except around foreign libraries is allowed."""
        code = '''
import requests

def good_function():
    try:
        response = requests.get("https://api.example.com")  # Foreign library
        return response.json()
    except requests.RequestException:
        return None
'''
        
        violations = self._analyze_code(code)
        
        # Should not detect violations for foreign library calls
        internal_violations = [
            v for v in violations 
            if v.violation_type == ViolationType.INTERNAL_CODE_IN_TRY
        ]
        assert len(internal_violations) == 0
    
    def test_bare_except_detection(self):
        """Test detection of bare except clauses."""
        code = '''
def bad_function():
    try:
        some_operation()
    except:  # Bare except
        pass
'''
        
        violations = self._analyze_code(code)
        
        # Should detect bare except
        bare_except_violations = [
            v for v in violations 
            if v.violation_type == ViolationType.BARE_EXCEPT
        ]
        assert len(bare_except_violations) > 0
    
    def test_broad_except_detection(self):
        """Test detection of overly broad exception handling."""
        code = '''
def bad_function():
    try:
        some_operation()
    except Exception:  # Too broad
        pass
'''
        
        violations = self._analyze_code(code)
        
        # Should detect broad except
        broad_except_violations = [
            v for v in violations 
            if v.violation_type == ViolationType.BROAD_EXCEPT
        ]
        assert len(broad_except_violations) > 0
    
    def test_specific_exceptions_allowed(self):
        """Test that specific exceptions are allowed."""
        code = '''
def good_function():
    try:
        with open("file.txt") as f:
            return f.read()
    except FileNotFoundError:  # Specific exception
        return None
    except PermissionError:    # Another specific exception
        return None
'''
        
        violations = self._analyze_code(code)
        
        # Should not detect violations for specific exceptions
        broad_except_violations = [
            v for v in violations 
            if v.violation_type == ViolationType.BROAD_EXCEPT
        ]
        assert len(broad_except_violations) == 0
    
    def test_system_exceptions_allowed(self):
        """Test that system exceptions are always allowed."""
        code = '''
def good_function():
    try:
        some_operation()
    except KeyboardInterrupt:  # System exception
        raise
    except SystemExit:         # System exception
        raise
'''
        
        violations = self._analyze_code(code)
        
        # Should not detect violations for system exceptions
        assert len(violations) == 0
    
    def test_configuration_loading(self):
        """Test configuration loading and customization."""
        config = AnalysisConfig()
        
        # Test default values
        assert 'requests' in config.allowed_foreign_libraries
        assert 'yaapp' in config.internal_modules
        assert 'KeyboardInterrupt' in config.allowed_exceptions
        
        # Test custom configuration
        custom_config = AnalysisConfig(
            allowed_foreign_libraries={'custom_lib'},
            internal_modules={'my_internal'},
            allowed_exceptions={'CustomException'}
        )
        
        assert custom_config.allowed_foreign_libraries == {'custom_lib'}
        assert custom_config.internal_modules == {'my_internal'}
        assert custom_config.allowed_exceptions == {'CustomException'}
    
    def test_reporter_console_format(self):
        """Test console report formatting."""
        reporter = ViolationReporter()
        
        # Test empty violations
        report = reporter.format_console_report([])
        assert "No violations found" in report
        
        # Test with violations (would need to create mock violations)
        # This is a basic test - more detailed testing would require mock violations
    
    def test_reporter_json_format(self):
        """Test JSON report formatting."""
        reporter = ViolationReporter()
        
        # Test empty violations
        json_report = reporter.format_json_report([])
        assert '"total_violations": 0' in json_report
        assert '"violations": []' in json_report
    
    def test_exclude_patterns(self):
        """Test that exclude patterns work correctly."""
        config = AnalysisConfig()
        analyzer = YaappStaticAnalyzer(config)
        
        # Test that test files are excluded by default
        assert analyzer._should_exclude_file("tests/test_something.py")
        assert analyzer._should_exclude_file("examples/example.py")
        assert not analyzer._should_exclude_file("src/yaapp/core.py")
    
    def _analyze_code(self, code: str):
        """Helper to analyze code string."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            try:
                analyzer = YaappStaticAnalyzer()
                violations = analyzer.analyze_file(f.name)
                return violations
            finally:
                os.unlink(f.name)


def test_yaapp_project_static_analysis():
    """Test static analysis on the actual yaapp project."""
    analyzer = YaappStaticAnalyzer()
    reporter = ViolationReporter()
    
    # Analyze the project
    violations = analyzer.analyze_project(".")
    
    # Generate report
    report = reporter.format_console_report(violations)
    print("\n" + "="*60)
    print("🔍 YAAPP PROJECT STATIC ANALYSIS")
    print("="*60)
    print(report)
    print("="*60)
    
    # Get summary
    summary = reporter.get_violation_summary(violations)
    print(f"\n📊 Summary: {summary['total_violations']} total violations")
    print(f"🚨 Errors: {summary['severity_breakdown']['error']}")
    print(f"⚠️  Warnings: {summary['severity_breakdown']['warning']}")
    
    # For now, just report violations but don't fail
    # In the future, we can make this stricter
    if violations:
        print(f"\n⚠️  Found {len(violations)} violations - review and fix as needed")
    else:
        print("\n✅ No violations found - excellent code quality!")


if __name__ == "__main__":
    # Run the project analysis directly
    test_yaapp_project_static_analysis()