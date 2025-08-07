#!/usr/bin/env python3
"""
Test the subprocess manager plugin integration with YAPP.
"""

import sys
import asyncio
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'src'))

from yaapp import Yaapp
from yaapp.plugins import SubprocessManager


def test_subprocess_manager_creation():
    """Test subprocess manager creation."""
    print("=== Testing SubprocessManager Creation ===")
    
    try:
        manager = SubprocessManager()
        print("✅ SubprocessManager created successfully")
        return True
    except Exception as e:
        print(f"❌ SubprocessManager creation failed: {e}")
        return False


def test_subprocess_manager_methods():
    """Test subprocess manager has expected methods."""
    print("\n=== Testing SubprocessManager Methods ===")
    
    try:
        manager = SubprocessManager()
        
        # Check for expected methods
        expected_methods = ['execute_call', 'execute_call_async', 'execute']
        missing_methods = []
        
        for method in expected_methods:
            if not hasattr(manager, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Missing methods: {missing_methods}")
            return False
        else:
            print(f"✅ All expected methods available: {expected_methods}")
            return True
            
    except Exception as e:
        print(f"❌ Method checking failed: {e}")
        return False


def test_simple_command_execution():
    """Test simple command execution via execute_call."""
    print("\n=== Testing Simple Command Execution ===")
    
    try:
        manager = SubprocessManager()
        
        # Test basic echo command using execute_call
        result = manager.execute_call(command="echo hello", timeout=5.0)
        
        if result is not None:
            print("✅ Command execution completed")
            print(f"✅ Result type: {type(result)}")
            return True
        else:
            print("❌ Command execution returned None")
            return False
            
    except Exception as e:
        print(f"❌ Command execution failed: {e}")
        return False


def test_yaapp_integration():
    """Test SubprocessManager integration with YAAPP."""
    print("\n=== Testing YAAPP Integration ===")
    
    try:
        app = Yaapp()
        manager = SubprocessManager()
        
        # Expose the subprocess manager
        app.expose(manager, name="subprocess")
        
        # Check if it's registered
        if "subprocess" in app._registry:
            print("✅ SubprocessManager registered with YAAPP")
            return True
        else:
            print("❌ SubprocessManager not found in YAAPP registry")
            return False
            
    except Exception as e:
        print(f"❌ YAAPP integration failed: {e}")
        return False


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