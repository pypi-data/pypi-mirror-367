#!/usr/bin/env python3
"""
Test runner script for Git Storage PoC.
Runs all tests and provides summary report.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        
        print(f"✅ SUCCESS ({duration:.2f}s)")
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        
        print(f"❌ FAILED ({duration:.2f}s)")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        
        return False


def main():
    """Run all tests and provide summary"""
    print("Git Storage PoC Test Runner")
    print("=" * 60)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    original_dir = Path.cwd()
    
    try:
        import os
        os.chdir(script_dir)
        
        # Test commands to run
        tests = [
            {
                "cmd": [sys.executable, "-m", "pytest", "test_git_storage.py", "-v", "--tb=short"],
                "description": "Git Storage Unit Tests"
            },
            {
                "cmd": [sys.executable, "-m", "pytest", "test_api.py", "-v", "--tb=short"],
                "description": "FastAPI Integration Tests"
            },
            {
                "cmd": [sys.executable, "-m", "pytest", "test_*.py", "-v", "--cov=.", "--cov-report=term-missing"],
                "description": "All Tests with Coverage"
            }
        ]
        
        # Run tests
        results = []
        total_start = time.time()
        
        for test in tests:
            success = run_command(test["cmd"], test["description"])
            results.append((test["description"], success))
        
        total_duration = time.time() - total_start
        
        # Summary report
        print(f"\n{'='*60}")
        print("TEST SUMMARY REPORT")
        print(f"{'='*60}")
        print(f"Total execution time: {total_duration:.2f}s")
        print()
        
        passed = 0
        failed = 0
        
        for description, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status:<12} {description}")
            
            if success:
                passed += 1
            else:
                failed += 1
        
        print(f"\nResults: {passed} passed, {failed} failed")
        
        if failed > 0:
            print("\n❌ Some tests failed. Please check the output above.")
            return 1
        else:
            print("\n✅ All tests passed successfully!")
            return 0
    
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return 1
    
    finally:
        os.chdir(original_dir)


if __name__ == "__main__":
    sys.exit(main())