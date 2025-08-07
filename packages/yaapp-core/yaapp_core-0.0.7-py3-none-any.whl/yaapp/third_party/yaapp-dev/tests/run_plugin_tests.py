#!/usr/bin/env python3
"""
Run tests for the async-first plugins we just fixed.
"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run all plugin tests."""
    print("🧪 Running Plugin Test Coverage")
    print("=" * 50)
    
    test_dirs = [
        "tests/plugins/registry",
        "tests/plugins/mesh", 
        "tests/plugins/portalloc",
        "tests/plugins/docker"
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_dir in test_dirs:
        print(f"\n📁 Testing {test_dir}")
        print("-" * 30)
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_dir, 
                "-v", 
                "--tb=short"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            
            if result.returncode == 0:
                print(f"✅ {test_dir}: PASSED")
                # Count passed tests
                passed = result.stdout.count(" PASSED")
                total_passed += passed
                print(f"   {passed} tests passed")
            else:
                print(f"❌ {test_dir}: FAILED")
                failed = result.stdout.count(" FAILED")
                total_failed += failed
                print(f"   {failed} tests failed")
                print("Error output:")
                print(result.stdout)
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ {test_dir}: ERROR - {e}")
            total_failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS:")
    print(f"✅ Total Passed: {total_passed}")
    print(f"❌ Total Failed: {total_failed}")
    
    if total_failed == 0:
        print("🎉 ALL PLUGIN TESTS PASSED!")
        return True
    else:
        print("⚠️  Some tests failed. Check output above.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)