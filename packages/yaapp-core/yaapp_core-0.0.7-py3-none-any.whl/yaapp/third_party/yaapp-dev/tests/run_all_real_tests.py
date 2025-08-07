#!/usr/bin/env python3
"""
REAL test runner that runs ALL tests, not just cherry-picked ones.
"""

import sys
import subprocess
import os
from pathlib import Path
import glob

def run_test(test_file):
    """Run a single test file and return success status."""
    print(f"Running {test_file}...", end=" ")
    
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
            print("✅")
            return True, None
        else:
            print("❌")
            error_msg = f"STDOUT: {result.stdout[-200:]}\nSTDERR: {result.stderr[-200:]}"
            return False, error_msg
            
    except subprocess.TimeoutExpired:
        print("⏰")
        return False, "TIMEOUT"
    except Exception as e:
        print("💥")
        return False, str(e)


def main():
    """Run ALL tests in the tests directory."""
    print("🧪 Running ALL Tests (The Real Deal)")
    print("=" * 60)
    
    # Find all test files
    test_files = []
    for pattern in ["tests/**/test_*.py", "tests/test_*.py"]:
        test_files.extend(glob.glob(pattern, recursive=True))
    
    test_files = sorted(set(test_files))  # Remove duplicates and sort
    
    print(f"Found {len(test_files)} test files")
    print("=" * 60)
    
    passed = 0
    failed = 0
    errors = []
    
    for test_file in test_files:
        success, error = run_test(test_file)
        if success:
            passed += 1
        else:
            failed += 1
            errors.append((test_file, error))
    
    print(f"\n{'='*60}")
    print(f"REAL TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests: {len(test_files)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {passed/len(test_files)*100:.1f}%")
    
    if failed > 0:
        print(f"\n💥 FAILED TESTS ({failed}):")
        for test_file, error in errors:
            print(f"❌ {test_file}")
            if error and len(error) < 500:
                print(f"   {error[:200]}...")
        
        print(f"\n💥 {failed}/{len(test_files)} TESTS FAILED!")
        return 1
    else:
        print("\n🎉 ALL TESTS PASSED!")
        return 0


if __name__ == '__main__':
    sys.exit(main())