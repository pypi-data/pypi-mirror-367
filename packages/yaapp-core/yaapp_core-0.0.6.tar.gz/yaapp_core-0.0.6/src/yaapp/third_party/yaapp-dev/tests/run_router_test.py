#!/usr/bin/env python3
"""
Simple test runner for router plugin test.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins', 'router'))

from test_router import TestRouter

def run_test():
    """Run the router plugin test."""
    test_instance = TestRouter()
    
    # List of test methods
    test_methods = [
        'test_add_route',
        'test_delete_route',
        'test_delete_nonexistent_route',
        'test_update_route',
        'test_update_nonexistent_route',
        'test_route_exact_match',
        'test_route_regex_match',
        'test_route_no_match',
        'test_route_handler_exception',
        'test_route_first_match_wins',
        'test_list_routes',
        'test_list_routes_empty',
        'test_multiple_routes_different_patterns',
        'test_route_with_complex_request',
        'test_route_pattern_order_matters',
        'test_empty_router',
        'test_route_with_none_request'
    ]
    
    passed = 0
    failed = 0
    
    for method_name in test_methods:
        try:
            # Set up for each test
            test_instance.setup_method()
            
            # Run the test method
            method = getattr(test_instance, method_name)
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