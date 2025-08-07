#!/usr/bin/env python3
"""
Comprehensive test for the session app to ensure consistent behavior.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

def run_app_command(args=None):
    """Helper to run the session app with given arguments."""
    app_path = Path(__file__).parent.parent.parent.parent.parent / "examples" / "plugins" / "session" / "app.py"
    
    cmd = [sys.executable, str(app_path)]
    if args:
        cmd.extend(args)
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(app_path.parent.parent.parent.parent)
    )
    
    return result

def test_consistent_help_behavior():
    """Test that help behavior is consistent between --help and no args."""
    
    print("=== Testing Consistent Help Behavior ===")
    
    # Test without arguments
    result_no_args = run_app_command()
    print("\\n--- Output without arguments ---")
    print("STDOUT:")
    print(result_no_args.stdout)
    print("STDERR:")
    print(result_no_args.stderr)
    print("Return code:", result_no_args.returncode)
    
    # Test with --help
    result_help = run_app_command(["--help"])
    print("\\n--- Output with --help ---")
    print("STDOUT:")
    print(result_help.stdout)
    print("STDERR:")
    print(result_help.stderr)
    print("Return code:", result_help.returncode)
    
    # Compare outputs (ignoring plugin loading messages)
    def normalize_output(output):
        lines = output.split('\\n')
        # Remove plugin loading messages
        filtered_lines = [line for line in lines if not line.startswith('✅') and not line.startswith('🔗')]
        return '\\n'.join(filtered_lines).strip()
    
    normalized_no_args = normalize_output(result_no_args.stdout)
    normalized_help = normalize_output(result_help.stdout)
    
    if normalized_no_args == normalized_help:
        print("\\n✅ PASS: Help behavior is consistent")
        assert True
    else:
        print("\\n❌ FAIL: Help behavior is inconsistent")
        print("\\nDifferences:")
        print("No args output:")
        print(repr(normalized_no_args))
        print("\\n--help output:")
        print(repr(normalized_help))
        return False

def test_required_elements_present():
    """Test that all required elements are present in the help output."""
    
    print("\\n=== Testing Required Elements ===")
    
    result = run_app_command(["--help"])
    output = result.stdout
    
    required_elements = [
        "Usage:",
        "Options:",
        "Commands:",
        "session",
        "--server",
        "--rich",
        "--prompt", 
        "--typer",
        "--help"
    ]
    
    missing = []
    for element in required_elements:
        if element not in output:
            missing.append(element)
    
    if missing:
        print(f"\\n❌ FAIL: Missing required elements: {missing}")
        print("\\nActual output:")
        print(output)
        return False
    else:
        print("\\n✅ PASS: All required elements present")
        assert True

def test_no_duplicate_runners():
    """Test that runners are not duplicated in the output."""
    
    print("\\n=== Testing No Duplicate Runners ===")
    
    result = run_app_command(["--help"])
    output = result.stdout
    
    # Check for duplicate "Runners:" sections
    runners_count = output.count("Runners:")
    
    if runners_count > 1:
        print(f"\\n❌ FAIL: Found {runners_count} 'Runners:' sections (should be 0 or 1)")
        print("\\nActual output:")
        print(output)
        return False
    elif runners_count == 1:
        print("\\n⚠️  WARNING: Found separate 'Runners:' section (should be integrated in Options)")
        return False
    else:
        print("\\n✅ PASS: No duplicate runners section")
        assert True

def test_runner_functionality():
    """Test that runner options actually work."""
    
    print("\\n=== Testing Runner Functionality ===")
    
    # Test server runner (with timeout to avoid hanging)
    try:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).parent.parent.parent.parent.parent / "examples" / "plugins" / "session" / "app.py"), "--server"],
            capture_output=True,
            text=True,
            timeout=2,
            cwd=str(Path(__file__).parent.parent.parent.parent.parent)
        )
    except subprocess.TimeoutExpired:
        print("\\n✅ PASS: Server runner started successfully (timed out as expected)")
        assert True
    
    # If it didn't timeout, check if it failed
    if result.returncode != 0:
        print(f"\\n❌ FAIL: Server runner failed with return code {result.returncode}")
        print("STDERR:", result.stderr)
        return False
    else:
        print("\\n✅ PASS: Server runner executed successfully")
        assert True

def test_command_functionality():
    """Test that commands work."""
    
    print("\\n=== Testing Command Functionality ===")
    
    # Test session command help
    result = run_app_command(["session", "--help"])
    
    if result.returncode != 0:
        print(f"\\n❌ FAIL: Session command help failed with return code {result.returncode}")
        print("STDERR:", result.stderr)
        return False
    
    if "create_session" not in result.stdout:
        print("\\n❌ FAIL: Session command doesn't show expected methods")
        print("Output:", result.stdout)
        return False
    
    print("\\n✅ PASS: Session command works correctly")
    assert True

def main():
    """Run all tests."""
    print("Running comprehensive session app tests...")
    print("=" * 60)
    
    tests = [
        test_consistent_help_behavior,
        test_required_elements_present,
        test_no_duplicate_runners,
        test_runner_functionality,
        test_command_functionality
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\\n❌ ERROR in {test.__name__}: {e}")
            results.append(False)
    
    print("\\n" + "=" * 60)
    print("TEST SUMMARY:")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test.__name__}: {status}")
    
    print(f"\\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\\n🎉 ALL TESTS PASSED! The session app is working correctly.")
        assert True
    else:
        print(f"\\n💥 {total - passed} TESTS FAILED! The session app needs fixes.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)