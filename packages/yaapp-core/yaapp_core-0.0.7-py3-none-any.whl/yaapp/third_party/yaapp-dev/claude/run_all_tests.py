#!/usr/bin/env python3
"""
Comprehensive test suite runner for YAPP framework.
Runs all tests to ensure framework quality and catch regressions.
"""

import sys
import os
import subprocess
import time
from pathlib import Path


def run_test_file(test_file: str, description: str) -> bool:
    """Run a test file and return success status."""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"File: {test_file}")
    print('='*60)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        duration = time.time() - start_time
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        success = result.returncode == 0
        
        if success:
            print(f"✅ {description} PASSED ({duration:.2f}s)")
        else:
            print(f"❌ {description} FAILED ({duration:.2f}s)")
            print(f"Return code: {result.returncode}")
        
        return success
        
    except subprocess.TimeoutExpired:
        print(f"❌ {description} TIMED OUT after 2 minutes")
        return False
    except Exception as e:
        print(f"❌ {description} ERROR: {e}")
        return False


def main():
    """Run all test suites."""
    print("🧪 YAPP Framework Complete Test Suite")
    print("Running comprehensive tests to ensure framework quality...")
    
    # Define all test files and descriptions
    test_suites = [
        ("test_integration.py", "Integration Tests - End-to-end functionality"),
        ("test_edge_cases.py", "Edge Case Tests - Error handling and boundaries"),
        ("test_async_integration.py", "Async Integration Tests - Async/sync dual interface"),
        ("test_server_mode.py", "Server Tests - FastAPI server functionality"),
        ("test_rpc_integration.py", "RPC Tests - RPC communication and AppProxy chaining"),
        ("test_registry_fix.py", "Registry Fix Tests - Basic functionality"),
        ("test_client.py", "Client Tests - AppProxy client functionality"),
        ("test_appproxy.py", "AppProxy Tests - Plugin system functionality"),
    ]
    
    # Optional tests (may not exist or may fail due to missing dependencies)
    optional_tests = [
        ("test_basic.py", "Basic Tests - Core functionality"),
        ("test_click_reflection.py", "Click Reflection Tests - CLI reflection"),
        ("test_async_compat.py", "Async Compatibility Tests - Core async utilities"),
        ("test_async_exposers.py", "Async Exposer Tests - Exposer async support"),
        ("test_async_core.py", "Async Core Tests - YAppCore async integration"),
    ]
    
    results = []
    start_time = time.time()
    
    print(f"\nFound {len(test_suites)} required test suites")
    print(f"Found {len(optional_tests)} optional test suites")
    
    # Run required tests
    print("\n" + "="*80)
    print("REQUIRED TEST SUITES")
    print("="*80)
    
    for test_file, description in test_suites:
        if Path(test_file).exists():
            success = run_test_file(test_file, description)
            results.append((test_file, description, success, True))  # True = required
        else:
            print(f"⚠️  {description} - File not found: {test_file}")
            results.append((test_file, description, False, True))
    
    # Run optional tests
    print("\n" + "="*80)
    print("OPTIONAL TEST SUITES")
    print("="*80)
    
    for test_file, description in optional_tests:
        if Path(test_file).exists():
            success = run_test_file(test_file, description)
            results.append((test_file, description, success, False))  # False = optional
        else:
            print(f"⚠️  {description} - File not found: {test_file}")
    
    # Test examples don't crash on import
    print("\n" + "="*80)
    print("EXAMPLE VALIDATION TESTS")
    print("="*80)
    
    examples = [
        "examples/data-analyzer/app.py",
        "examples/task-manager/app.py", 
        "examples/file-processor/app.py"
    ]
    
    for example in examples:
        if Path(example).exists():
            print(f"\nTesting {example} import...")
            result = subprocess.run(
                [sys.executable, "-c", f"import sys; sys.path.insert(0, 'src'); import importlib.util; spec = importlib.util.spec_from_file_location('example', '{example}'); module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); print('✅ Import successful')"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {example} imports successfully")
                results.append((example, "Example Import", True, False))
            else:
                print(f"❌ {example} import failed:")
                print(result.stderr)
                results.append((example, "Example Import", False, False))
        else:
            print(f"⚠️  Example not found: {example}")
    
    # Summary
    total_time = time.time() - start_time
    
    print("\n" + "="*80)
    print("TEST SUITE SUMMARY")
    print("="*80)
    
    required_tests = [(f, d, s, r) for f, d, s, r in results if r]
    optional_tests = [(f, d, s, r) for f, d, s, r in results if not r]
    
    required_passed = sum(1 for _, _, success, _ in required_tests if success)
    required_total = len(required_tests)
    
    optional_passed = sum(1 for _, _, success, _ in optional_tests if success)
    optional_total = len(optional_tests)
    
    print(f"Required Tests: {required_passed}/{required_total} passed")
    print(f"Optional Tests: {optional_passed}/{optional_total} passed")
    print(f"Total Time: {total_time:.2f} seconds")
    
    # Show failed tests
    failed_tests = [(f, d) for f, d, s, r in results if not s]
    if failed_tests:
        print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
        for test_file, description in failed_tests:
            print(f"  - {description} ({test_file})")
    
    # Show passed tests
    passed_tests = [(f, d) for f, d, s, r in results if s]
    if passed_tests:
        print(f"\n✅ PASSED TESTS ({len(passed_tests)}):")
        for test_file, description in passed_tests:
            print(f"  - {description}")
    
    # Final verdict
    print("\n" + "="*80)
    
    required_all_passed = required_passed == required_total
    
    if required_all_passed:
        print("🎉 ALL REQUIRED TESTS PASSED!")
        print("The YAPP framework is working correctly.")
        
        if optional_total > 0:
            print(f"Optional tests: {optional_passed}/{optional_total} passed")
        
        print("\n✨ Framework Quality: EXCELLENT")
        return True
    else:
        failed_required = required_total - required_passed
        print(f"💥 {failed_required} REQUIRED TESTS FAILED!")
        print("Critical issues detected in the framework.")
        
        print("\n⚠️  Framework Quality: POOR - NEEDS FIXES")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)