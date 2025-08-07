#!/usr/bin/env python3
"""
Quick status check of key tests to see overall progress.
"""

import subprocess
import sys
from pathlib import Path

def test_file(test_path, description):
    """Test a single file and return status."""
    try:
        result = subprocess.run(
            [sys.executable, test_path],
            cwd=Path(__file__).parent.parent,
            env={'PYTHONPATH': 'src'},
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return f"✅ {description}"
        else:
            return f"❌ {description}"
    except subprocess.TimeoutExpired:
        return f"⏰ {description} (timeout)"
    except Exception as e:
        return f"💥 {description} (error: {e})"

def main():
    """Check status of key tests."""
    print("🔍 Quick Status Check of Key Tests")
    print("=" * 50)
    
    key_tests = [
        ("tests/unit/test_basic_functionality.py", "Basic Functionality"),
        ("tests/unit/test_config.py", "Configuration"),
        ("tests/unit/test_execution_strategy.py", "Execution Strategy"),
        ("tests/integration/test_comprehensive.py", "Comprehensive Integration"),
        ("tests/integration/test_async_core.py", "Async Core"),
        ("tests/integration/test_bug_fixes.py", "Bug Fixes"),
        ("tests/integration/test_new_fixes.py", "New Fixes"),
        ("tests/integration/test_subprocess_plugin.py", "Subprocess Plugin"),
        ("tests/plugins/storage/integration/test_yaapp_integration.py", "Storage Plugin"),
        ("tests/run_discovery_tests.py", "Discovery System"),
    ]
    
    passed = 0
    total = len(key_tests)
    
    for test_path, description in key_tests:
        status = test_file(test_path, description)
        print(status)
        if "✅" in status:
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Key Tests Status: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    if passed >= total * 0.8:  # 80% or better
        print("🎉 Core functionality is working well!")
    elif passed >= total * 0.6:  # 60% or better
        print("👍 Most core functionality is working")
    else:
        print("⚠️  Some core functionality needs attention")

if __name__ == '__main__':
    main()