"""
Pytest plugin for yaapp static analysis.

Add this to conftest.py or install as a pytest plugin to run static analysis as part of tests.
"""

import pytest
from pathlib import Path
import sys

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))

from static_analysis import YaappStaticAnalyzer, AnalysisConfig, ViolationReporter


def pytest_addoption(parser):
    """Add command line options for static analysis."""
    group = parser.getgroup("yaapp-static-analysis")
    
    group.addoption(
        "--static-analysis",
        action="store_true",
        default=False,
        help="Run yaapp static analysis"
    )
    
    group.addoption(
        "--static-analysis-fail",
        action="store_true", 
        default=False,
        help="Fail tests if static analysis violations found"
    )
    
    group.addoption(
        "--static-analysis-config",
        help="Path to static analysis configuration file"
    )


def pytest_configure(config):
    """Configure pytest for static analysis."""
    config.addinivalue_line(
        "markers", 
        "static_analysis: mark test as static analysis test"
    )


def pytest_collection_modifyitems(config, items):
    """Add static analysis test if requested."""
    if config.getoption("--static-analysis"):
        # Create static analysis test
        static_test = StaticAnalysisTest.from_config(config)
        items.append(static_test)


class StaticAnalysisTest:
    """Pytest test item for static analysis."""
    
    def __init__(self, name, parent, config_path=None, fail_on_violations=False):
        self.name = name
        self.parent = parent
        self.config_path = config_path
        self.fail_on_violations = fail_on_violations
        
        # Initialize analyzer
        analysis_config = AnalysisConfig()
        self.analyzer = YaappStaticAnalyzer(analysis_config)
        self.reporter = ViolationReporter()
    
    @classmethod
    def from_config(cls, pytest_config):
        """Create static analysis test from pytest config."""
        return cls(
            name="static_analysis",
            parent=None,
            config_path=pytest_config.getoption("--static-analysis-config"),
            fail_on_violations=pytest_config.getoption("--static-analysis-fail")
        )
    
    def runtest(self):
        """Run static analysis."""
        # Analyze the project
        violations = self.analyzer.analyze_project(".")
        
        # Generate report
        report = self.reporter.format_console_report(violations)
        print("\n" + "="*60)
        print("🔍 YAAPP STATIC ANALYSIS REPORT")
        print("="*60)
        print(report)
        print("="*60)
        
        # Fail if violations found and fail_on_violations is True
        if violations and self.fail_on_violations:
            summary = self.reporter.get_violation_summary(violations)
            pytest.fail(
                f"Static analysis found {summary['total_violations']} violations "
                f"({summary['severity_breakdown']['error']} errors, "
                f"{summary['severity_breakdown']['warning']} warnings)"
            )
    
    def repr_failure(self, excinfo):
        """Represent test failure."""
        return str(excinfo.value)
    
    def reportinfo(self):
        """Report test info."""
        return self.name, 0, "yaapp static analysis"


# Standalone test function that can be called directly
def test_static_analysis():
    """Standalone static analysis test."""
    analyzer = YaappStaticAnalyzer()
    reporter = ViolationReporter()
    
    # Analyze the project
    violations = analyzer.analyze_project(".")
    
    # Generate report
    report = reporter.format_console_report(violations)
    print("\n" + "="*60)
    print("🔍 YAAPP STATIC ANALYSIS REPORT")
    print("="*60)
    print(report)
    print("="*60)
    
    # Get summary for assertion
    summary = reporter.get_violation_summary(violations)
    
    # Assert no critical violations (errors)
    critical_violations = [
        v for v in violations 
        if v.violation_type.value in ['forbidden_try_except', 'internal_code_in_try']
    ]
    
    assert len(critical_violations) == 0, (
        f"Found {len(critical_violations)} critical static analysis violations. "
        f"See report above for details."
    )