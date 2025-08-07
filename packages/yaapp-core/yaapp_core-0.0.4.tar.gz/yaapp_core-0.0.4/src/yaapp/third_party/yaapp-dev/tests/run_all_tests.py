#!/usr/bin/env python3
"""
Simple test runner to check overall test status.
Runs key tests to verify the discovery system didn't break existing functionality.
"""

import sys
import subprocess
import os
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def run_test(test_file, description):
    """Run a single test file and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"File: {test_file}")
    print('='*60)
    
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = 'src'
        
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=Path(__file__).parent.parent,
            env=env,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ PASSED")
            return True
        else:
            print("❌ FAILED")
            if result.stdout:
                print("STDOUT:", result.stdout[-500:])  # Last 500 chars
            if result.stderr:
                print("STDERR:", result.stderr[-500:])
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False


def main():
    """Run key tests to verify system health."""
    print("🧪 Running Key Tests to Verify System Health")
    print("=" * 60)
    
    tests = [
        # Core functionality tests
        ("tests/unit/test_basic_functionality.py", "Basic Functionality"),
        ("tests/unit/test_execution_strategy.py", "Execution Strategy"),
        ("tests/unit/test_config.py", "Configuration System"),
        
        # Discovery system tests
        ("tests/run_discovery_tests.py", "Discovery System"),
        ("tests/unit/test_singleton_instance.py", "Singleton Instance"),
        
        # Integration tests
        ("tests/integration/test_comprehensive.py", "Comprehensive Integration"),
        ("tests/integration/test_async_core.py", "Async Core"),
        ("tests/plugins/storage/integration/test_yaapp_integration.py", "Storage Plugin Integration"),
        
        # Argument parsing and bug fixes
        ("tests/unit/test_argument_parsing_fix.py", "Argument Parsing Fix"),
    ]
    
    passed = 0
    failed = 0
    
    for test_file, description in tests:
        if run_test(test_file, description):
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL KEY TESTS PASSED!")
        print("✅ Discovery system integration successful")
        print("✅ No regressions detected in core functionality")
        return 0
    else:
        print(f"\n💥 {failed} TESTS FAILED!")
        print("❌ Some functionality may be broken")
        return 1


if __name__ == '__main__':
    sys.exit(main())