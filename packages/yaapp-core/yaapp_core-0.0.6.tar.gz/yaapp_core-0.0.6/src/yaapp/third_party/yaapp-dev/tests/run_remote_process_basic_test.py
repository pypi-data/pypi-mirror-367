#!/usr/bin/env python3
"""
Simple test runner for remote process basic test.
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins', 'remote_process'))

from test_remote_process_basic import TestRemoteProcessBasic, TestRemoteProcessIntegration

def run_test():
    """Run the remote process basic tests."""
    
    # Test basic functionality
    basic_test = TestRemoteProcessBasic()
    basic_methods = [
        'test_factory_function',
        'test_initial_state',
        'test_send_input_no_process',
        'test_send_signal_no_process',
        'test_stop_process_no_process',
        'test_tail_output_no_process'
    ]
    
    # Test integration
    integration_test = TestRemoteProcessIntegration()
    integration_methods = [
        'test_echo_command_integration',
        # Skip async test for now
    ]
    
    passed = 0
    failed = 0
    
    print("=== Testing Basic Functionality ===")
    for method_name in basic_methods:
        try:
            basic_test.setup_method()
            method = getattr(basic_test, method_name)
            method()
            print(f"✅ {method_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {method_name}: {e}")
            failed += 1
    
    print("\n=== Testing Integration ===")
    for method_name in integration_methods:
        try:
            integration_test.setup_method()
            method = getattr(integration_test, method_name)
            
            # Check if it's an async method
            if asyncio.iscoroutinefunction(method):
                asyncio.run(method())
            else:
                method()
                
            print(f"✅ {method_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {method_name}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)