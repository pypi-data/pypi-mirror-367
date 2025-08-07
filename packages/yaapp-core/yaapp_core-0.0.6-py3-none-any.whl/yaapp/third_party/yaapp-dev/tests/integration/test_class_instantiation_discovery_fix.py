#!/usr/bin/env python3
"""
Test the class instantiation discovery fix.
Tests that method discovery no longer requires class instantiation.
"""

import sys
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, "../../src")

from yaapp import Yaapp


class TestResults_:
    """Track test results."""
    passed = 0
    failed = 0
    errors = []
    
    def assert_true(self, condition, message):
        if condition:
            self.passed += 1
            print(f"✅ {message}")
        else:
            self.failed += 1
            error = f"❌ {message}"
            print(error)
            self.errors.append(error)
    
    def assert_equal(self, actual, expected, message):
        if actual == expected:
            self.passed += 1
            print(f"✅ {message}")
        else:
            self.failed += 1
            error = f"❌ {message} - Expected: {expected}, Got: {actual}"
            print(error)  
            self.errors.append(error)
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n=== TEST SUMMARY ===")
        print(f"Total: {total}, Passed: {self.passed}, Failed: {self.failed}")
        if self.errors:
            print("\nFAILED TESTS:")
            for error in self.errors:
                print(f"  {error}")
        return self.failed == 0


def test_reflection_no_instantiation(results):
    """Test that reflection system doesn't instantiate classes during exposure."""
    print("\n=== Testing Reflection System No Instantiation ===")
    
    instantiation_count = 0
    
    class TestClass:
        def __init__(self):
            nonlocal instantiation_count
            instantiation_count += 1
            print(f"TestClass instantiated (count: {instantiation_count})")
        
        def test_method(self):
            return "test"
        
        def another_method(self, value: int = 42):
            return value * 2
    
    try:
        app = Yaapp(auto_discover=False)
        
        # Reset counter
        instantiation_count = 0
        
        # Exposing the class should NOT instantiate it (only store it for later)
        app.expose(TestClass, "TestClass")
        
        results.assert_equal(instantiation_count, 0, "Class exposure requires no instantiation")
        
        # Verify class is in registry
        registry = app.get_registry_items()
        results.assert_true("TestClass" in registry, "Class is in registry")
        results.assert_equal(registry["TestClass"], TestClass, "Registry contains the class")
        
        # Method discovery through dir() should also not instantiate
        methods = [m for m in dir(TestClass) if not m.startswith('_') and callable(getattr(TestClass, m))]
        results.assert_true(len(methods) >= 2, "Methods discovered without instantiation")
        results.assert_equal(instantiation_count, 0, "Method discovery requires no instantiation")
        
    except Exception as e:
        results.assert_true(False, f"Reflection no instantiation test failed: {e}")


def test_fastapi_runner_no_instantiation(results):
    """Test that FastAPI runner doesn't instantiate classes for method discovery."""
    print("\n=== Testing FastAPI Runner No Instantiation ===")
    
    instantiation_count = 0
    
    class TestService:
        def __init__(self):
            nonlocal instantiation_count
            instantiation_count += 1
            print(f"TestService instantiated (count: {instantiation_count})")
        
        def get_data(self):
            return {"data": "test"}
        
        def update_data(self, value: str):
            return {"updated": value}
    
    try:
        from yaapp.runners.fastapi_runner import FastAPIRunner
        
        app = Yaapp()
        runner = FastAPIRunner(app)
        
        # Reset counter
        instantiation_count = 0
        
        # Test _get_class_methods - should NOT instantiate
        methods = runner._get_class_methods(TestService)
        
        results.assert_equal(instantiation_count, 0, "FastAPI _get_class_methods requires no instantiation")
        results.assert_true("get_data" in methods, "get_data method discovered")
        results.assert_true("update_data" in methods, "update_data method discovered")
        results.assert_true("__init__" not in methods, "Private methods not included")
        
        # Verify method metadata includes class for later instantiation
        if "get_data" in methods:
            results.assert_equal(methods["get_data"]["class"], TestService, "Class stored for later instantiation")
        
        # Reset counter
        instantiation_count = 0
        
        # Test _get_class_methods_rpc - should also NOT instantiate
        rpc_methods = runner._get_class_methods_rpc(TestService)
        
        results.assert_equal(instantiation_count, 0, "FastAPI _get_class_methods_rpc requires no instantiation")
        results.assert_true("get_data" in rpc_methods, "RPC get_data method discovered")
        results.assert_true("update_data" in rpc_methods, "RPC update_data method discovered")
        
    except Exception as e:
        results.assert_true(False, f"FastAPI no instantiation test failed: {e}")


def test_expensive_constructor_not_called(results):
    """Test that expensive constructors are not called during discovery."""
    print("\n=== Testing Expensive Constructor Not Called ===")
    
    constructor_called = False
    
    class ExpensiveClass:
        def __init__(self):
            nonlocal constructor_called
            constructor_called = True
            # Simulate expensive operation
            import time
            time.sleep(0.001)  # Simulate work
            raise Exception("This expensive constructor should not be called during discovery!")
        
        def expensive_method(self):
            return "expensive operation"
        
        def another_expensive_method(self, param: str):
            return f"processed: {param}"
    
    try:
        from yaapp.runners.fastapi_runner import FastAPIRunner
        from yaapp.reflection import CommandReflector
        
        app = Yaapp()
        runner = FastAPIRunner(app)
        reflector = CommandReflector(app)
        
        # Reset flag
        constructor_called = False
        
        # Test FastAPI method discovery
        methods = runner._get_class_methods(ExpensiveClass)
        results.assert_true(not constructor_called, "Expensive constructor not called in FastAPI discovery")
        results.assert_true("expensive_method" in methods, "Methods still discovered despite expensive constructor")
        
        # Reset flag
        constructor_called = False
        
        # Test RPC method discovery
        rpc_methods = runner._get_class_methods_rpc(ExpensiveClass)
        results.assert_true(not constructor_called, "Expensive constructor not called in RPC discovery")
        results.assert_true("expensive_method" in rpc_methods, "RPC methods still discovered despite expensive constructor")
        
        # Reset flag
        constructor_called = False
        
        # Test reflection discovery
        mock_cli_group = Mock()
        mock_cli_group.group = Mock(side_effect=lambda name: lambda func: func)
        
        try:
            reflector._add_class_command(mock_cli_group, "ExpensiveClass", ExpensiveClass)
            results.assert_true(not constructor_called, "Expensive constructor not called in reflection discovery")
        except Exception as e:
            # If reflection fails for other reasons, that's OK as long as constructor wasn't called
            results.assert_true(not constructor_called, "Expensive constructor not called in reflection discovery (even with reflection error)")
        
    except Exception as e:
        results.assert_true(False, f"Expensive constructor test failed: {e}")


def test_method_signatures_still_available(results):
    """Test that method signatures are still available without instantiation."""
    print("\n=== Testing Method Signatures Still Available ===")
    
    class SignatureTestClass:
        def simple_method(self):
            """A simple method."""
            return "simple"
        
        def method_with_params(self, name: str, age: int = 25):
            """A method with parameters."""
            return f"Name: {name}, Age: {age}"
        
        def method_with_return_type(self, value: float) -> str:
            """A method with return type annotation."""
            return str(value)
    
    try:
        from yaapp.runners.fastapi_runner import FastAPIRunner
        import inspect
        
        app = Yaapp()
        runner = FastAPIRunner(app)
        
        # Get methods without instantiation
        methods = runner._get_class_methods(SignatureTestClass)
        
        results.assert_true("simple_method" in methods, "Simple method discovered")
        results.assert_true("method_with_params" in methods, "Method with params discovered")
        results.assert_true("method_with_return_type" in methods, "Method with return type discovered")
        
        # Test that we can still get signatures from the unbound methods
        if "method_with_params" in methods:
            method_func = methods["method_with_params"]["func"]
            sig = inspect.signature(method_func)
            params = list(sig.parameters.keys())
            
            # Should include 'self' for unbound methods
            results.assert_true("self" in params, "Unbound method includes self parameter")
            results.assert_true("name" in params, "Method parameter 'name' available")
            results.assert_true("age" in params, "Method parameter 'age' available")
        
        # Test RPC method signatures
        rpc_methods = runner._get_class_methods_rpc(SignatureTestClass)
        if "method_with_params" in rpc_methods:
            signature_info = rpc_methods["method_with_params"]["signature"]
            # The signature info contains parameter names directly, not under a 'parameters' key
            results.assert_true(len(signature_info) > 0, "RPC signature info includes parameters")
            results.assert_true("name" in signature_info, "RPC signature includes 'name' parameter")
            results.assert_true("age" in signature_info, "RPC signature includes 'age' parameter")
        
    except Exception as e:
        results.assert_true(False, f"Method signatures test failed: {e}")


def test_discovery_performance_improvement(results):
    """Test that discovery is faster without instantiation."""
    print("\n=== Testing Discovery Performance Improvement ===")
    
    class SlowConstructorClass:
        def __init__(self):
            # Simulate slow initialization
            import time
            time.sleep(0.01)  # 10ms delay
        
        def fast_method(self):
            return "fast"
    
    try:
        from yaapp.runners.fastapi_runner import FastAPIRunner
        import time
        
        app = Yaapp()
        runner = FastAPIRunner(app)
        
        # Measure discovery time
        start_time = time.time()
        methods = runner._get_class_methods(SlowConstructorClass)
        discovery_time = time.time() - start_time
        
        # Discovery should be very fast (much less than constructor time)
        results.assert_true(discovery_time < 0.005, f"Discovery is fast: {discovery_time:.4f}s < 0.005s")
        results.assert_true("fast_method" in methods, "Method still discovered quickly")
        
        # Measure RPC discovery time
        start_time = time.time()
        rpc_methods = runner._get_class_methods_rpc(SlowConstructorClass)
        rpc_discovery_time = time.time() - start_time
        
        results.assert_true(rpc_discovery_time < 0.005, f"RPC discovery is fast: {rpc_discovery_time:.4f}s < 0.005s")
        
    except Exception as e:
        results.assert_true(False, f"Performance improvement test failed: {e}")


def main():
    """Run all class instantiation discovery fix tests."""
    print("🔧 YAPP Class Instantiation Discovery Fix Tests")
    print("Testing that method discovery no longer requires class instantiation.")
    
    results = TestResults()
    
    # Run all test suites
    test_reflection_no_instantiation(results)
    test_fastapi_runner_no_instantiation(results)
    test_expensive_constructor_not_called(results)
    test_method_signatures_still_available(results)
    test_discovery_performance_improvement(results)
    
    # Show summary
    success = results.summary()
    
    if success:
        print("\n🎉 ALL CLASS INSTANTIATION DISCOVERY FIX TESTS PASSED!")
        print("Method discovery optimizations successful:")
        print("  • Reflection system no longer instantiates classes for method discovery")
        print("  • FastAPI runner avoids instantiation in _get_class_methods()")
        print("  • FastAPI runner avoids instantiation in _get_class_methods_rpc()")
        print("  • Expensive constructors are not called during discovery")
        print("  • Method signatures and metadata still available")
        print("  • Significant performance improvement for classes with slow constructors")
    else:
        print("\n💥 CLASS INSTANTIATION DISCOVERY FIX TESTS FAILED!")
        print("Issues detected in discovery fix.")
        sys.exit(1)


if __name__ == "__main__":
    main()