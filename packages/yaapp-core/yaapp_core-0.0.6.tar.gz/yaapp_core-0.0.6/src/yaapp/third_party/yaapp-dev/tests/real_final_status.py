#!/usr/bin/env python3
"""
Get the REAL final status of ALL tests.
"""

import subprocess
import sys
import glob
from pathlib import Path

def run_test(test_path):
    """Test a single file quickly."""
    try:
        result = subprocess.run(
            [sys.executable, test_path],
            cwd=Path(__file__).parent.parent,
            env={'PYTHONPATH': 'src'},
            capture_output=True,
            text=True,
            timeout=15
        )
        return result.returncode == 0
    except:
        return False

def main():
    """Get real status of ALL tests."""
    print("📊 REAL FINAL STATUS - ALL TESTS")
    print("=" * 50)
    
    # Find all test files
    test_files = sorted(glob.glob("tests/**/test_*.py", recursive=True))
    
    print(f"Found {len(test_files)} test files")
    print("Testing...")
    
    passed = 0
    failed = 0
    
    for i, test_file in enumerate(test_files):
        print(f"[{i+1}/{len(test_files)}] {test_file}...", end=" ")
        
        if run_test(test_file):
            print("✅")
            passed += 1
        else:
            print("❌")
            failed += 1
    
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "=" * 50)
    print(f"FINAL RESULTS:")
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! Nearly all tests passing!")
    elif success_rate >= 80:
        print("🚀 GREAT! Most tests passing!")
    elif success_rate >= 70:
        print("👍 GOOD! Majority of tests passing!")
    elif success_rate >= 60:
        print("⚠️  FAIR! More than half passing!")
    else:
        print("💥 NEEDS WORK! Many tests still failing!")

if __name__ == '__main__':
    main()