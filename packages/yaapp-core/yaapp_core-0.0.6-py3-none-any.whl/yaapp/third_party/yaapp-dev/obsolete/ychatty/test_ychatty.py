#!/usr/bin/env python3
"""
Quick test script for ychatty to ensure it works before publishing.
"""

import subprocess
import sys
from pathlib import Path


def test_import():
    """Test that ychatty can be imported."""
    try:
        import ychatty
        print("✅ Import test passed")
        print(f"   Version: {ychatty.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False


def test_cli_help():
    """Test that the CLI help works."""
    try:
        result = subprocess.run(
            ["uv", "run", "ychatty", "--help"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        if "ychatty - A simple and friendly command-line chat interface" in result.stdout:
            print("✅ CLI help test passed")
            return True
        else:
            print("❌ CLI help test failed: unexpected output")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ CLI help test failed: {e}")
        return False


def test_version():
    """Test that the version command works."""
    try:
        result = subprocess.run(
            ["uv", "run", "ychatty", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        if "0.1.0" in result.stdout:
            print("✅ Version test passed")
            return True
        else:
            print("❌ Version test failed: unexpected output")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Version test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Testing ychatty before publishing...")
    print()
    
    tests = [
        test_import,
        test_cli_help,
        test_version,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready to publish!")
        return True
    else:
        print("❌ Some tests failed. Please fix before publishing.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)