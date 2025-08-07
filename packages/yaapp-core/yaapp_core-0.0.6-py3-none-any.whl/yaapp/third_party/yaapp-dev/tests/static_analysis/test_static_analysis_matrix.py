"""
Static Analysis Violation Matrix - Breakdown by Category and Source File

This test creates a detailed matrix of violations to make fixing easier.
"""

import pytest
from pathlib import Path
import sys
from collections import defaultdict

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from static_analysis import YaappStaticAnalyzer, AnalysisConfig, ViolationReporter
from static_analysis.rules import ViolationType


def test_static_analysis_violation_matrix():
    """Create a detailed matrix of violations by category and file."""
    analyzer = YaappStaticAnalyzer()
    reporter = ViolationReporter()
    
    # Analyze the project
    violations = analyzer.analyze_project(".")
    
    # Create violation matrix
    matrix = defaultdict(lambda: defaultdict(list))
    
    for violation in violations:
        file_path = violation.file_path
        violation_type = violation.violation_type.value
        matrix[violation_type][file_path].append(violation)
    
    # Print detailed matrix
    print("\n" + "="*80)
    print("🔍 YAAPP STATIC ANALYSIS VIOLATION MATRIX")
    print("="*80)
    
    total_violations = len(violations)
    total_files = len(set(v.file_path for v in violations))
    
    print(f"📊 SUMMARY: {total_violations} violations across {total_files} files")
    print()
    
    # Sort violation types by severity and count
    violation_type_counts = defaultdict(int)
    for violation in violations:
        violation_type_counts[violation.violation_type.value] += 1
    
    # Define severity order
    severity_order = [
        'internal_code_in_try',      # 🚨 Critical
        'forbidden_try_except',      # 🚨 Critical  
        'broad_except',              # ⚠️ Warning
        'bare_except',               # ⚠️ Warning
        'missing_specific_exception' # ⚠️ Warning
    ]
    
    for violation_type in severity_order:
        if violation_type not in matrix:
            continue
            
        count = violation_type_counts[violation_type]
        severity = "🚨 CRITICAL" if violation_type in ['internal_code_in_try', 'forbidden_try_except'] else "⚠️  WARNING"
        
        print(f"\n{severity} - {violation_type.upper()}: {count} violations")
        print("-" * 60)
        
        # Sort files by number of violations (descending)
        files_with_violations = sorted(
            matrix[violation_type].items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        for file_path, file_violations in files_with_violations:
            print(f"  📄 {file_path}: {len(file_violations)} violations")
            
            # Show first few line numbers for context
            line_numbers = sorted([v.line_number for v in file_violations[:5]])
            if len(file_violations) > 5:
                line_numbers_str = f"Lines {', '.join(map(str, line_numbers))}... (+{len(file_violations)-5} more)"
            else:
                line_numbers_str = f"Lines {', '.join(map(str, line_numbers))}"
            
            print(f"     {line_numbers_str}")
    
    print("\n" + "="*80)
    print("🎯 FIXING PRIORITY RECOMMENDATIONS")
    print("="*80)
    
    # Critical violations first
    critical_violations = [
        v for v in violations 
        if v.violation_type.value in ['internal_code_in_try', 'forbidden_try_except']
    ]
    
    if critical_violations:
        print(f"\n🚨 CRITICAL: Fix {len(critical_violations)} critical violations first!")
        critical_files = defaultdict(int)
        for v in critical_violations:
            critical_files[v.file_path] += 1
        
        print("   Priority files:")
        for file_path, count in sorted(critical_files.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {file_path}: {count} critical violations")
    
    # Most problematic files
    file_violation_counts = defaultdict(int)
    for violation in violations:
        file_violation_counts[violation.file_path] += 1
    
    print(f"\n📊 TOP 10 FILES WITH MOST VIOLATIONS:")
    top_files = sorted(file_violation_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (file_path, count) in enumerate(top_files, 1):
        print(f"   {i:2d}. {file_path}: {count} violations")
    
    # Violation type breakdown
    print(f"\n📈 VIOLATION TYPE BREAKDOWN:")
    for violation_type in severity_order:
        if violation_type in violation_type_counts:
            count = violation_type_counts[violation_type]
            percentage = (count / total_violations) * 100
            print(f"   {violation_type:25s}: {count:3d} ({percentage:5.1f}%)")
    
    print("\n" + "="*80)
    print("🛠️  FIXING STRATEGY")
    print("="*80)
    
    print("\n1. 🚨 CRITICAL VIOLATIONS (Fix immediately):")
    print("   - internal_code_in_try: Remove try/except around yaapp internal code")
    print("   - forbidden_try_except: Only use try/except for foreign library calls")
    
    print("\n2. ⚠️  HIGH PRIORITY (Fix next):")
    print("   - broad_except: Replace 'except Exception:' with specific exceptions")
    print("   - bare_except: Replace 'except:' with specific exception types")
    
    print("\n3. 📝 MEDIUM PRIORITY (Improve gradually):")
    print("   - missing_specific_exception: Add specific exception handling for foreign calls")
    
    print("\n4. 📁 SUGGESTED FILE ORDER:")
    print("   - Start with files having critical violations")
    print("   - Then tackle files with most total violations")
    print("   - Focus on core files (src/yaapp/core.py, src/yaapp/app.py, etc.)")
    
    print("\n" + "="*80)
    
    # Assert that we should fail if there are critical violations
    if critical_violations:
        pytest.fail(
            f"🚨 CRITICAL: Found {len(critical_violations)} critical static analysis violations! "
            f"These must be fixed before merging. See matrix above for details."
        )
    
    # For now, don't fail on warnings, but report them
    warning_violations = [
        v for v in violations 
        if v.violation_type.value not in ['internal_code_in_try', 'forbidden_try_except']
    ]
    
    if warning_violations:
        print(f"\n⚠️  Found {len(warning_violations)} warning violations - should be fixed gradually")
    
    # Uncomment this line to make the test fail on ANY violations:
    # assert len(violations) == 0, f"Found {len(violations)} static analysis violations"


def test_critical_violations_only():
    """Test that fails only on critical violations."""
    analyzer = YaappStaticAnalyzer()
    violations = analyzer.analyze_project(".")
    
    # Only fail on critical violations
    critical_violations = [
        v for v in violations 
        if v.violation_type.value in ['internal_code_in_try', 'forbidden_try_except']
    ]
    
    if critical_violations:
        reporter = ViolationReporter()
        report = reporter.format_console_report(critical_violations)
        print("\n🚨 CRITICAL VIOLATIONS FOUND:")
        print(report)
        
        assert len(critical_violations) == 0, (
            f"Found {len(critical_violations)} critical static analysis violations! "
            f"These MUST be fixed before merging."
        )


def test_file_specific_violations():
    """Test violations for specific important files."""
    analyzer = YaappStaticAnalyzer()
    
    # Important core files that should have minimal violations
    important_files = [
        "src/yaapp/core.py",
        "src/yaapp/app.py", 
        "src/yaapp/config.py",
        "src/yaapp/reflection.py"
    ]
    
    for file_path in important_files:
        if Path(file_path).exists():
            violations = analyzer.analyze_file(file_path)
            
            # Check for critical violations in core files
            critical_violations = [
                v for v in violations 
                if v.violation_type.value in ['internal_code_in_try', 'forbidden_try_except']
            ]
            
            print(f"\n📄 {file_path}: {len(violations)} total, {len(critical_violations)} critical")
            
            # Core files should have zero critical violations
            assert len(critical_violations) == 0, (
                f"Core file {file_path} has {len(critical_violations)} critical violations! "
                f"Core files must be clean."
            )


if __name__ == "__main__":
    # Run the matrix analysis directly
    test_static_analysis_violation_matrix()