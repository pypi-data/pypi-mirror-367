#!/usr/bin/env python3
"""
Comprehensive test runner for the reorganized YAAPP test structure.
Runs all tests in the organized directory structure.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def run_test_file(test_file: Path, description: str) -> bool:
    """Run a test file and return success status."""
    print(f"\n{'='*80}")
    print(f"Running {description}")
    print(f"File: {test_file}")
    print('='*80)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ["uv", "run", "python", str(test_file)],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
            cwd=str(Path.cwd())
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ PASSED in {elapsed:.2f}s")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ FAILED in {elapsed:.2f}s")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ TIMEOUT after 120s")
        return False
    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False

def main():
    """Run all organized tests."""
    print("🧪 YAAPP Organized Test Suite")
    print("="*80)
    
    start_time = time.time()
    
    # Define test categories and their files
    test_categories = {
        "Unit Tests": [
            ("tests/unit/test_basic_functionality.py", "Basic YAAPP Functionality"),
            ("tests/unit/test_execution_parameter.py", "Execution Parameter Tests"),
            ("tests/unit/test_reflection_fix.py", "Reflection System Fix Tests"),
        ],
        "Async Tests": [
            ("tests/async/test_async_compat_fix.py", "Async Compatibility Fix Tests"),
            ("tests/async/test_async_detection.py", "Async Detection Tests"),
        ],
        "Configuration Tests": [
            ("tests/config/test_enhanced_config.py", "Enhanced Configuration Tests"),
        ],
        "Bug Fixes": [
            ("tests/fixes/test_fastapi_execution_fix.py", "FastAPI Execution Fix Tests"),
            ("tests/fixes/test_sync_execution_contexts.py", "Sync Execution Context Tests"),
        ],
        "Integration Tests": [
            ("tests/integration/test_api_endpoints.py", "API Endpoints Tests"),
            ("tests/integration/test_migration.py", "Migration Tests"),
            ("tests/integration/test_run.py", "Run Method Tests"),
            ("tests/integration/test_subprocess_plugin.py", "Subprocess Plugin Tests"),
        ],
    }
    
    # Track results
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    # Run tests by category
    for category, tests in test_categories.items():
        print(f"\n🏷️  {category}")
        print("="*80)
        
        for test_file, description in tests:
            test_path = Path(test_file)
            if test_path.exists():
                total_tests += 1
                if run_test_file(test_path, description):
                    passed_tests += 1
                else:
                    failed_tests.append((test_file, description))
            else:
                print(f"⚠️  SKIP: {test_file} (not found)")
    
    # Print summary
    elapsed = time.time() - start_time
    failed_count = len(failed_tests)
    
    print(f"\n{'='*80}")
    print("🏁 TEST SUMMARY")
    print('='*80)
    print(f"Total tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_count}")
    print(f"⏱️  Total time: {elapsed:.2f}s")
    
    if failed_tests:
        print(f"\n❌ Failed tests:")
        for test_file, description in failed_tests:
            print(f"   • {description} ({test_file})")
        print("\n💡 Check individual test output above for details.")
        return 1
    else:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ Organized test structure is working correctly")
        return 0

if __name__ == "__main__":
    sys.exit(main())