"""
Static Analysis Violation Matrix - Verbose Version with Better Error Messages

This test creates a detailed matrix of violations with comprehensive error reporting.
"""

import pytest
from pathlib import Path
import sys
from collections import defaultdict

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from static_analysis import YaappStaticAnalyzer, AnalysisConfig, ViolationReporter
from static_analysis.rules import ViolationType


def test_static_analysis_violation_matrix_verbose():
    """Create a detailed matrix of violations with comprehensive error reporting."""
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
    print("🔍 YAAPP STATIC ANALYSIS VIOLATION MATRIX (VERBOSE)")
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
    
    # Separate critical and warning violations
    critical_violations = [
        v for v in violations 
        if v.violation_type.value in ['internal_code_in_try', 'forbidden_try_except']
    ]
    
    warning_violations = [
        v for v in violations 
        if v.violation_type.value not in ['internal_code_in_try', 'forbidden_try_except']
    ]
    
    print(f"🚨 CRITICAL VIOLATIONS: {len(critical_violations)} (MUST FIX BEFORE MERGING)")
    print(f"⚠️  WARNING VIOLATIONS: {len(warning_violations)} (SHOULD FIX GRADUALLY)")
    print()
    
    # Show detailed breakdown
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
    print("🎯 YAAPP CODE QUALITY RULES EXPLANATION")
    print("="*80)
    
    print("\n📋 YAAPP'S CORE RULE:")
    print("   'try/except blocks should ONLY protect calls to FOREIGN libraries'")
    print("   'try/except around INTERNAL yaapp code is FORBIDDEN'")
    
    print("\n🔍 WHAT COUNTS AS FOREIGN vs INTERNAL:")
    print("   ✅ FOREIGN (allowed in try/except):")
    print("      - requests, httpx, aiohttp (HTTP libraries)")
    print("      - json, yaml, xml (data parsing)")
    print("      - os, sys, pathlib (system calls)")
    print("      - asyncio, threading (concurrency)")
    print("      - click, typer (CLI libraries)")
    print("      - fastapi, flask (web frameworks)")
    print("   ")
    print("   ❌ INTERNAL (forbidden in try/except):")
    print("      - yaapp.expose(), yaapp.run()")
    print("      - yaapp.core.*, yaapp.app.*")
    print("      - yaapp.reflection.*, yaapp.exposers.*")
    print("      - Any yaapp.* module calls")
    
    print("\n💡 WHY THIS RULE EXISTS:")
    print("   - Internal yaapp code should be reliable and not need try/catch")
    print("   - try/except should only handle external failures (network, files, etc.)")
    print("   - This keeps error handling focused and prevents masking internal bugs")
    
    print("\n" + "="*80)
    print("🛠️  DETAILED FIXING INSTRUCTIONS")
    print("="*80)
    
    if critical_violations:
        print(f"\n🚨 CRITICAL VIOLATIONS TO FIX IMMEDIATELY ({len(critical_violations)} total):")
        print("   These MUST be fixed before merging!")
        print()
        
        for i, violation in enumerate(critical_violations, 1):
            print(f"   {i}. 📄 {violation.file_path}:{violation.line_number}")
            print(f"      🔴 Type: {violation.violation_type.value}")
            print(f"      📝 Issue: {violation.message}")
            print(f"      💡 Fix: {violation.suggestion}")
            
            if violation.code_snippet:
                print(f"      📋 Current Code:")
                for line in violation.code_snippet.split('\n')[:3]:  # Show first 3 lines
                    if line.strip():
                        print(f"         {line}")
                if len(violation.code_snippet.split('\n')) > 3:
                    print(f"         ... (see file for complete code)")
            
            print(f"      🔧 How to fix:")
            if 'yaapp.expose' in violation.code_snippet:
                print(f"         - Remove the try/except around yaapp.expose()")
                print(f"         - OR move yaapp.expose() outside the try block")
                print(f"         - OR add specific error handling for the actual foreign call")
            else:
                print(f"         - Remove try/except around internal yaapp code")
                print(f"         - OR ensure try/except only protects foreign library calls")
            print()
    
    if warning_violations:
        print(f"\n⚠️  WARNING VIOLATIONS ({len(warning_violations)} total):")
        print("   These should be fixed gradually for better code quality")
        print()
        
        warning_summary = defaultdict(int)
        for v in warning_violations:
            warning_summary[v.violation_type.value] += 1
        
        for violation_type, count in warning_summary.items():
            print(f"   - {violation_type}: {count} violations")
            if violation_type == 'broad_except':
                print(f"     Fix: Replace 'except Exception:' with specific exceptions")
            elif violation_type == 'bare_except':
                print(f"     Fix: Replace 'except:' with specific exception types")
            elif violation_type == 'missing_specific_exception':
                print(f"     Fix: Add specific exception handling for foreign library calls")
    
    print("\n" + "="*80)
    print("🚀 VERIFICATION COMMANDS")
    print("="*80)
    
    print("\n📋 To check your fixes:")
    print("   python tools/run_static_analysis.py")
    print("   python tools/run_static_analysis.py src/yaapp/exposers/custom.py")
    print()
    print("📋 To run this test again:")
    print("   uv run pytest tests/static_analysis/test_static_analysis_matrix_verbose.py -v -s")
    print()
    print("📋 To see only critical violations:")
    print("   uv run pytest tests/static_analysis/test_static_analysis_matrix_verbose.py::test_critical_violations_only -v -s")
    
    print("\n" + "="*80)
    
    # Create comprehensive error message for critical violations
    if critical_violations:
        error_msg = "🚨 CRITICAL STATIC ANALYSIS VIOLATIONS FOUND!"
        error_msg += f"\n\n📊 SUMMARY: {len(critical_violations)} critical violations across {len(set(v.file_path for v in critical_violations))} files"
        error_msg += f"\n\n🔴 WHY THIS IS CRITICAL:"
        error_msg += f"\n   These violations break yaapp's core rule:"
        error_msg += f"\n   'try/except blocks should ONLY protect foreign library calls'"
        error_msg += f"\n   'try/except around internal yaapp code is FORBIDDEN'"
        
        error_msg += f"\n\n📝 VIOLATIONS TO FIX:"
        for i, violation in enumerate(critical_violations, 1):
            error_msg += f"\n   {i}. {violation.file_path}:{violation.line_number}"
            error_msg += f"\n      Type: {violation.violation_type.value}"
            error_msg += f"\n      Issue: {violation.message}"
            error_msg += f"\n      Fix: {violation.suggestion}"
            if violation.code_snippet:
                # Show first line of code snippet
                first_line = violation.code_snippet.split('\n')[0].strip()
                error_msg += f"\n      Code: {first_line}..."
        
        error_msg += f"\n\n🔧 HOW TO FIX:"
        error_msg += f"\n   1. Open the file(s) listed above"
        error_msg += f"\n   2. Remove the try/except block around yaapp internal code"
        error_msg += f"\n   3. OR move the yaapp code outside the try/except"
        error_msg += f"\n   4. OR ensure the try/except only protects foreign library calls"
        
        error_msg += f"\n\nℹ️  NOTE: {len(warning_violations)} warning violations remain but won't block merging"
        error_msg += f"\n\n🚀 After fixing, run: python tools/run_static_analysis.py to verify"
        
        pytest.fail(error_msg)
    
    # For now, don't fail on warnings, but report them
    if warning_violations:
        print(f"\n⚠️  Found {len(warning_violations)} warning violations - should be fixed gradually")


def test_critical_violations_only_verbose():
    """Test that fails only on critical violations with detailed explanation."""
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
        
        # Create detailed error message
        error_msg = "🚨 CRITICAL STATIC ANALYSIS VIOLATIONS DETECTED!"
        error_msg += f"\n\n📊 Found {len(critical_violations)} critical violations that MUST be fixed before merging"
        
        error_msg += f"\n\n🔴 YAAPP'S CORE RULE VIOLATION:"
        error_msg += f"\n   Rule: 'try/except blocks should ONLY protect foreign library calls'"
        error_msg += f"\n   Violation: 'try/except around internal yaapp code is FORBIDDEN'"
        
        error_msg += f"\n\n📝 SPECIFIC VIOLATIONS:"
        for i, violation in enumerate(critical_violations, 1):
            error_msg += f"\n   {i}. File: {violation.file_path}:{violation.line_number}"
            error_msg += f"\n      Problem: {violation.message}"
            error_msg += f"\n      Solution: {violation.suggestion}"
        
        error_msg += f"\n\n🔧 QUICK FIX GUIDE:"
        error_msg += f"\n   1. Open: {critical_violations[0].file_path}"
        error_msg += f"\n   2. Go to line: {critical_violations[0].line_number}"
        error_msg += f"\n   3. Remove try/except around yaapp.expose() call"
        error_msg += f"\n   4. Run: python tools/run_static_analysis.py to verify"
        
        error_msg += f"\n\n💡 WHY THIS MATTERS:"
        error_msg += f"\n   - Internal yaapp code should be reliable"
        error_msg += f"\n   - try/except should only handle external failures"
        error_msg += f"\n   - This prevents masking internal bugs"
        
        assert len(critical_violations) == 0, error_msg


def test_show_specific_violation_details():
    """Show detailed information about the specific critical violation."""
    analyzer = YaappStaticAnalyzer()
    violations = analyzer.analyze_file("src/yaapp/exposers/custom.py")
    
    critical_violations = [
        v for v in violations 
        if v.violation_type.value in ['internal_code_in_try', 'forbidden_try_except']
    ]
    
    if critical_violations:
        violation = critical_violations[0]
        
        print("\n" + "="*60)
        print("🔍 DETAILED VIOLATION ANALYSIS")
        print("="*60)
        
        print(f"\n📄 File: {violation.file_path}")
        print(f"📍 Location: Line {violation.line_number}, Column {violation.column_number}")
        print(f"🔴 Type: {violation.violation_type.value}")
        print(f"📝 Message: {violation.message}")
        print(f"💡 Suggestion: {violation.suggestion}")
        
        print(f"\n📋 Problematic Code:")
        if violation.code_snippet:
            for i, line in enumerate(violation.code_snippet.split('\n')):
                if line.strip():
                    line_num = violation.line_number + i
                    marker = "👉" if i == 0 else "  "
                    print(f"   {marker} {line_num:3d}: {line}")
        
        print(f"\n🔧 How to Fix This Specific Issue:")
        print(f"   The code is using try/except around 'yaapp.expose(proxy_func, name)'")
        print(f"   This violates yaapp's rule because yaapp.expose() is internal code")
        print(f"   ")
        print(f"   Option 1 - Remove try/except:")
        print(f"   ```python")
        print(f"   # Just call it directly")
        print(f"   yaapp.expose(proxy_func, name)")
        print(f"   ```")
        print(f"   ")
        print(f"   Option 2 - Move yaapp.expose outside try/except:")
        print(f"   ```python")
        print(f"   # First do the risky foreign operation")
        print(f"   try:")
        print(f"       # ... some foreign library call ...")
        print(f"   except SpecificException as e:")
        print(f"       print(f'Foreign operation failed: {{e}}')")
        print(f"       return")
        print(f"   ")
        print(f"   # Then do the safe yaapp operation")
        print(f"   yaapp.expose(proxy_func, name)")
        print(f"   ```")
        
        print(f"\n🎯 Why This Rule Exists:")
        print(f"   - yaapp.expose() should be reliable and not fail")
        print(f"   - If it does fail, we want to see the real error, not mask it")
        print(f"   - try/except should only protect against external failures")
        print(f"   - This keeps error handling focused and debugging easier")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    # Run the verbose matrix analysis directly
    test_static_analysis_violation_matrix_verbose()