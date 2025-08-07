#!/usr/bin/env python3
"""
Tests for the three critical bug fixes:
1. Async compatibility silent failures
2. Context navigation string manipulation
3. Registry architecture issues
"""

import sys
import math
import asyncio
import inspect
from pathlib import Path

# Add src to path
sys.path.insert(0, "../../src")

from yaapp import Yaapp
from yaapp.async_compat import async_compatible
from yaapp.context_tree import ContextTree, ContextNode
from yaapp.core import YaappCore


class BugFixTestResults:
    """Track bug fix test results."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def assert_true(self, condition, message):
        if condition:
            self.passed += 1
            print(f"✅ {message}")
        else:
            self.failed += 1
            error = f"❌ {message}"
            print(error)
            self.errors.append(error)
    
    def assert_false(self, condition, message):
        self.assert_true(not condition, message)
    
    def assert_equal(self, actual, expected, message):
        if actual == expected:
            self.passed += 1
            print(f"✅ {message}")
        else:
            self.failed += 1
            error = f"❌ {message} - Expected: {expected}, Got: {actual}"
            print(error)
            self.errors.append(error)
    
    def assert_raises(self, exception_type, func, message):
        try:
            func()
            self.failed += 1
            error = f"❌ {message} - Expected {exception_type.__name__} but no exception was raised"
            print(error)
            self.errors.append(error)
        except exception_type:
            self.passed += 1
            print(f"✅ {message}")
        except Exception as e:
            self.failed += 1
            error = f"❌ {message} - Expected {exception_type.__name__} but got {type(e).__name__}: {e}"
            print(error)
            self.errors.append(error)
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n=== BUG FIX TEST SUMMARY ===")
        print(f"Total: {total}, Passed: {self.passed}, Failed: {self.failed}")
        if self.errors:
            print("\nFAILED TESTS:")
            for error in self.errors:
                print(f"  {error}")
        return self.failed == 0


def test_async_compatibility_fixes(results):
    """Test async compatibility no longer has silent failures."""
    print("\n=== Testing Async Compatibility Fixes ===")
    
    # Test 1: Built-in functions should raise ValueError
    try:
        async_compatible(math.sqrt)
        results.assert_true(False, "Built-in function should raise ValueError")
    except ValueError as e:
        results.assert_true("Built-in function" in str(e) or "wrapper approach" in str(e), "Built-in function raises proper error")
    except Exception as e:
        results.assert_true(False, f"Built-in function raised unexpected error: {e}")
    
    # Test 2: Bound methods should raise ValueError
    class TestClass:
        def method(self, x):
            return x * 2
    
    obj = TestClass()
    try:
        async_compatible(obj.method)
        results.assert_true(False, "Bound method should raise ValueError")
    except ValueError as e:
        results.assert_true("Bound method" in str(e), "Bound method raises proper error")
    except Exception as e:
        results.assert_true(False, f"Bound method raised unexpected error: {e}")
    
    # Test 3: Regular functions should work fine
    def regular_func(x):
        return x + 1
    
    try:
        decorated = async_compatible(regular_func)
        results.assert_true(hasattr(decorated, 'async_version'), "Regular function gets async_version")
        results.assert_true(hasattr(decorated, 'is_async'), "Regular function gets is_async attribute")
        results.assert_false(decorated.is_async, "Regular function is_async is False")
    except Exception as e:
        results.assert_true(False, f"Regular function decoration failed: {e}")
    
    # Test 4: Async functions should work fine
    async def async_func(x):
        return x + 1
    
    try:
        decorated = async_compatible(async_func)
        results.assert_true(hasattr(decorated, 'sync'), "Async function gets sync version")
        results.assert_true(hasattr(decorated, 'is_async'), "Async function gets is_async attribute")
        results.assert_true(decorated.is_async, "Async function is_async is True")
    except Exception as e:
        results.assert_true(False, f"Async function decoration failed: {e}")
    
    # Test 5: Verify sync wrapper works
    try:
        result = decorated.sync(5)
        results.assert_equal(result, 6, "Sync wrapper executes correctly")
    except Exception as e:
        results.assert_true(False, f"Sync wrapper execution failed: {e}")


def test_context_tree_functionality(results):
    """Test context tree replaces string manipulation."""
    print("\n=== Testing Context Tree Functionality ===")
    
    # Test 1: Basic tree operations
    tree = ContextTree()
    
    # Add items
    tree.add_item("math.add", lambda x, y: x + y)
    tree.add_item("math.subtract", lambda x, y: x - y)
    tree.add_item("utils.format", lambda s: s.upper())
    tree.add_item("simple_func", lambda: "hello")
    
    results.assert_equal(len(tree.get_all_paths()), 4, "All paths added correctly")
    
    # Test 2: Root context items
    root_items = tree.get_current_context_items()
    results.assert_true("simple_func" in root_items, "Simple function visible in root")
    results.assert_false("add" in root_items, "Nested function not directly visible in root")
    
    # Test 3: Context navigation
    results.assert_true(tree.can_enter_context("math"), "Can enter math context")
    results.assert_true(tree.enter_context("math"), "Successfully enter math context")
    
    math_items = tree.get_current_context_items()
    results.assert_true("add" in math_items, "Add function visible in math context")
    results.assert_true("subtract" in math_items, "Subtract function visible in math context")
    results.assert_false("format" in math_items, "Utils functions not visible in math context")
    
    # Test 4: Context path tracking
    current_path = tree.get_current_context_path()
    results.assert_equal(current_path, ["math"], "Current context path is correct")
    
    # Test 5: Exit context
    results.assert_true(tree.exit_context(), "Successfully exit context")
    results.assert_equal(tree.get_current_context_path(), [], "Back to root context")
    
    # Test 6: Leaf command detection
    results.assert_true(tree.enter_context("math"), "Enter math context again")
    results.assert_true(tree.is_leaf_command("add"), "Add is leaf command")
    results.assert_false(tree.can_enter_context("add"), "Cannot enter leaf command")
    
    # Test 7: Edge cases that caused string manipulation bugs
    tree.add_item("mathematics.sqrt", lambda x: x ** 0.5)  # Should not conflict with "math"
    tree.add_item("a.b.c", lambda: "deep")
    tree.add_item("a.bc.e", lambda: "different")  # Should not conflict with "a.b"
    
    tree.reset_to_root()
    results.assert_true(tree.enter_context("a"), "Enter 'a' context")
    a_items = tree.get_current_context_items()
    results.assert_false("bc" in a_items, "a.bc not confused with a.b context")
    
    results.assert_true(tree.enter_context("b"), "Enter 'a.b' context")
    ab_items = tree.get_current_context_items()
    results.assert_true("c" in ab_items, "a.b.c visible in a.b context")
    results.assert_false("e" in ab_items, "a.bc.e not visible in a.b context")


def test_registry_architecture_fixes(results):
    """Test registry now stores exposer objects properly."""
    print("\n=== Testing Registry Architecture Fixes ===")
    
    # Test 1: Registry stores (object, exposer) pairs
    core = YaappCore()
    
    def test_func(x):
        return x * 2
    
    class TestClass:
        def method(self, y):
            return y + 1
    
    # Expose items
    core.expose(test_func, "test_func")
    core.expose(TestClass, "TestClass")
    
    # Test registry structure
    results.assert_true("test_func" in core._registry, "Function in registry")
    results.assert_true("TestClass" in core._registry, "Class in registry")
    
    # Check that registry stores tuples
    func_entry = core._registry["test_func"]
    results.assert_true(isinstance(func_entry, tuple), "Registry entry is tuple")
    results.assert_equal(len(func_entry), 2, "Registry tuple has 2 elements")
    
    obj, exposer = func_entry
    results.assert_equal(obj, test_func, "First element is original object")
    results.assert_true(hasattr(exposer, 'run'), "Second element is exposer with run method")
    
    # Test 2: Execution through exposers
    try:
        result = core._execute_from_registry("test_func", x=5)
        if result.is_ok():
            results.assert_equal(result.unwrap(), 10, "Function execution through exposer works")
        else:
            results.assert_true(False, f"Function execution failed: {result.as_error}")
    except Exception as e:
        results.assert_true(False, f"Function execution failed: {e}")
    
    # Test 3: Backward compatibility methods
    raw_func_result = core.get_registry_item("test_func")
    if raw_func_result.is_ok():
        results.assert_equal(raw_func_result.unwrap(), test_func, "get_registry_item returns raw object")
    else:
        results.assert_true(False, f"get_registry_item failed: {raw_func_result.as_error}")
    
    func_exposer_result = core.get_registry_exposer("test_func")
    if func_exposer_result.is_ok():
        results.assert_true(hasattr(func_exposer_result.unwrap(), 'run'), "get_registry_exposer returns exposer")
    else:
        results.assert_true(False, f"get_registry_exposer failed: {func_exposer_result.as_error}")
    
    all_items = core.get_registry_items()
    results.assert_true("test_func" in all_items, "get_registry_items includes function")
    results.assert_equal(all_items["test_func"], test_func, "get_registry_items returns raw objects")
    
    # Test 4: Different exposer types for different objects
    func_exposer_result = core.get_registry_exposer("test_func")
    class_exposer_result = core.get_registry_exposer("TestClass")
    
    if func_exposer_result.is_ok() and class_exposer_result.is_ok():
        func_exposer = func_exposer_result.unwrap()
        class_exposer = class_exposer_result.unwrap()
        results.assert_true(type(func_exposer).__name__ == "FunctionExposer", "Function uses FunctionExposer")
        results.assert_true(type(class_exposer).__name__ == "ClassExposer", "Class uses ClassExposer")
    else:
        results.assert_true(False, "Failed to get exposers for type checking")
    
    # Test 5: Custom exposer functionality
    class CustomObject:
        def execute_call(self, **kwargs):
            return f"Custom execution with {kwargs}"
    
    custom_obj = CustomObject()
    core.expose(custom_obj, "custom_obj", custom=True)
    
    try:
        result = core._execute_from_registry("custom_obj", param="test")
        if result.is_ok():
            unwrapped = result.unwrap()
            results.assert_true("Custom execution" in unwrapped, "Custom exposer execution works")
            results.assert_true("test" in unwrapped, "Custom exposer receives parameters")
        else:
            results.assert_true(False, f"Custom exposer execution failed: {result.as_error}")
    except Exception as e:
        results.assert_true(False, f"Custom exposer execution failed: {e}")


def test_integration_with_yapp(results):
    """Test that bug fixes work with full YApp integration."""
    print("\n=== Testing Integration with YApp ===")
    
    app = Yaapp()
    
    # Test 1: Async compatibility errors are properly handled
    def regular_function(x):
        return x + 1
    
    try:
        app.expose(regular_function)
        results.assert_true(True, "Regular function exposure works")
    except Exception as e:
        results.assert_true(False, f"Regular function exposure failed: {e}")
    
    # Test 2: Context navigation uses tree
    app.expose({"math": {"add": lambda x, y: x + y, "multiply": lambda x, y: x * y}})
    
    # Verify context tree is populated
    math_items = app._context_tree.get_children_at_path(["math"])
    results.assert_true(len(math_items) >= 2, "Math namespace has functions in context tree")
    
    # Test 3: Registry architecture maintains backward compatibility
    registry_items = app.get_registry_items()
    results.assert_true("regular_function" in registry_items, "Regular function in backward compatible registry")
    results.assert_true("math.add" in registry_items, "Nested function in backward compatible registry")
    
    # Test 4: Execution works through new architecture
    try:
        result = app._execute_from_registry("regular_function", x=5)
        if result.is_ok():
            results.assert_equal(result.unwrap(), 6, "Execution through new architecture works")
        else:
            results.assert_true(False, f"Execution through new architecture failed: {result.as_error}")
    except Exception as e:
        results.assert_true(False, f"Execution through new architecture failed: {e}")


def test_error_cases_and_edge_cases(results):
    """Test error handling and edge cases for all fixes."""
    print("\n=== Testing Error Cases and Edge Cases ===")
    
    # Test 1: Context tree error handling
    tree = ContextTree()
    
    # Empty path
    try:
        tree.add_item("", lambda: None)
        results.assert_true(False, "Empty path should raise ValueError")
    except ValueError:
        results.assert_true(True, "Empty path raises ValueError")
    except Exception as e:
        results.assert_true(False, f"Empty path raised unexpected error: {e}")
    
    # Test 2: Registry error handling
    core = YaappCore()
    
    # Execute non-existent function
    try:
        result = core._execute_from_registry("nonexistent")
        if result.is_ok():
            results.assert_true(False, "Non-existent function should return error")
        else:
            results.assert_true("not found" in result.as_error, "Non-existent function returns error")
    except Exception as e:
        results.assert_true(False, f"Non-existent function raised unexpected error: {e}")
    
    # Test 3: Async compatibility with complex objects
    class ComplexClass:
        @staticmethod
        def static_method(x):
            return x
        
        @classmethod
        def class_method(cls, x):
            return x
    
    # These should work (not bound methods)
    try:
        async_compatible(ComplexClass.static_method)
        results.assert_true(True, "Static method decoration works")
    except Exception as e:
        results.assert_true(False, f"Static method decoration failed: {e}")
    
    try:
        async_compatible(ComplexClass.class_method)
        results.assert_true(False, "Class method should raise ValueError (it's a bound method)")
    except ValueError as e:
        results.assert_true("Bound method" in str(e), "Class method raises proper error (it's bound)")
    except Exception as e:
        results.assert_true(False, f"Class method raised unexpected error: {e}")
    
    # Test 4: Context tree deep nesting
    tree = ContextTree()
    deep_path = "a.b.c.d.e.f.g.h.i.j"
    tree.add_item(deep_path, lambda: "deep")
    
    results.assert_true(tree.get_item(deep_path) is not None, "Deep nesting works")
    
    # Navigate deep
    path_parts = deep_path.split(".")
    for part in path_parts[:-1]:  # All but last
        if tree.can_enter_context(part):
            tree.enter_context(part)
    
    final_items = tree.get_current_context_items()
    results.assert_true(path_parts[-1] in final_items, "Deep navigation reaches final item")


def main():
    """Run all bug fix tests."""
    print("🐛 YAPP Bug Fix Tests")
    print("Testing fixes for async compatibility, context navigation, and registry architecture")
    
    results = BugFixTestResults()
    
    # Run all test suites
    test_async_compatibility_fixes(results)
    test_context_tree_functionality(results)
    test_registry_architecture_fixes(results)
    test_integration_with_yapp(results)
    test_error_cases_and_edge_cases(results)
    
    # Show summary
    success = results.summary()
    
    if success:
        print("\n🎉 ALL BUG FIX TESTS PASSED!")
        print("All three critical bugs have been successfully fixed:")
        print("  ✅ Async compatibility no longer fails silently")
        print("  ✅ Context navigation uses efficient tree structure")
        print("  ✅ Registry properly stores and uses exposer objects")
    else:
        print("\n💥 BUG FIX TESTS FAILED!")
        print("Some fixes are not working correctly.")
        sys.exit(1)


if __name__ == "__main__":
    main()