#!/usr/bin/env python3
"""
Test the subprocess manager plugin integration with YAPP.
"""

import sys
import asyncio
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from yaapp import Yaapp
from yaapp.plugins.remote.plugin import RemoteProcess as SubprocessManager


def test_subprocess_manager_creation():
    """Test subprocess manager creation."""
    print("=== Testing SubprocessManager Creation ===")
    
    try:
        manager = SubprocessManager()
        print("✅ SubprocessManager created successfully")
        assert True
    except Exception as e:
        print(f"❌ SubprocessManager creation failed: {e}")
        assert False, "Test failed"


def test_subprocess_manager_methods():
    """Test subprocess manager has expected methods."""
    print("\n=== Testing SubprocessManager Methods ===")
    
    try:
        manager = SubprocessManager()
        
        # Check for actual methods (SubprocessManager is alias for RemoteProcess)
        expected_methods = ['start_process', 'inject_command', 'tail_output', 'stop_process', 'is_running']
        missing_methods = []
        
        for method in expected_methods:
            if not hasattr(manager, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Missing methods: {missing_methods}")
            assert False, "Test failed"
        else:
            print(f"✅ All expected methods available: {expected_methods}")
            assert True
            
    except Exception as e:
        print(f"❌ Method checking failed: {e}")
        assert False, "Test failed"


def test_simple_command_execution():
    """Test simple command execution via start_process."""
    print("\n=== Testing Simple Command Execution ===")
    
    try:
        manager = SubprocessManager()
        
        # Test with a simple command that exits immediately (like echo)
        # This should work but process will exit immediately
        result = manager.start_process("echo hello")
        
        if result is not None:
            if "Successfully started" in result:
                print("✅ Command started successfully")
                print(f"✅ Result type: {type(result)}")
                assert True
            elif "process exited with code 0" in result:
                # This is actually expected for echo command
                print("✅ Command executed and exited normally (expected for echo)")
                print(f"✅ Result: {result}")
                assert True
            else:
                print(f"❌ Unexpected result: {result}")
                assert False, "Test failed"
        else:
            print("❌ Command execution returned None")
            assert False, "Test failed"
            
    except Exception as e:
        print(f"❌ Command execution failed: {e}")
        assert False, "Test failed"


def test_yaapp_integration():
    """Test SubprocessManager integration with YAAPP."""
    print("\n=== Testing YAAPP Integration ===")
    
    try:
        app = Yaapp(auto_discover=False)
        manager = SubprocessManager()
        
        # Expose the subprocess manager
        app.expose(manager, name="subprocess")
        
        # Check if it's registered
        if "subprocess" in app._registry:
            print("✅ SubprocessManager registered with YAAPP")
            assert True
        else:
            print("❌ SubprocessManager not found in YAAPP registry")
            assert False, "Test failed"
            
    except Exception as e:
        print(f"❌ YAAPP integration failed: {e}")
        assert False, "Test failed"


if __name__ == "__main__":
    print("🧪 Testing YAAPP Subprocess Manager Plugin")
    print("="*60)
    
    tests = [
        test_subprocess_manager_creation,
        test_subprocess_manager_methods,
        test_simple_command_execution,
        test_yaapp_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n{'='*60}")
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 ALL SUBPROCESS PLUGIN TESTS PASSED!")
        exit(0)
    else:
        print("❌ SOME SUBPROCESS PLUGIN TESTS FAILED!")
        exit(1)