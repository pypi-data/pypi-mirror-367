#!/usr/bin/env python3
"""
Simple test runner for issues plugin test.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'plugins', 'issues'))
from test_issues_plugin import TestIssuesPlugin

def run_test():
    """Run the issues plugin test."""
    test_instance = TestIssuesPlugin()
    
    # List of test methods
    test_methods = [
        'test_create_issue',
        'test_get_issue', 
        'test_get_nonexistent_issue',
        'test_update_issue',
        'test_update_nonexistent_issue',
        'test_delete_issue',
        'test_list_issues',
        'test_list_issues_with_status_filter',
        'test_list_issues_with_assignee_filter',
        'test_assign_issue',
        'test_close_issue',
        'test_reopen_issue',
        'test_add_comment',
        'test_get_comments',
        'test_add_comment_to_nonexistent_issue',
        'test_get_comments_for_nonexistent_issue',
        'test_issue_timestamps',
        'test_issue_id_format',
        'test_default_values'
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