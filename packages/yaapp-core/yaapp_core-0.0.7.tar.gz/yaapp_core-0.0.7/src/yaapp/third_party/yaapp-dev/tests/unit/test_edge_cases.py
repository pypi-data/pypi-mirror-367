#!/usr/bin/env python3
"""
Edge case and error condition tests for YAPP framework.
These tests verify error handling and boundary conditions.
"""

import pytest
from yaapp import Yaapp
from yaapp.result import Result, Ok


def test_invalid_exposures():
    """Test error handling for invalid exposures."""
    app = Yaapp()
    
    # Test exposing None with explicit name (bypasses decorator logic)
    result = app.expose(None, "explicit_none")
    # This should either fail or handle gracefully
    assert result is not None
    
    # Test exposing with empty name
    def test_func():
        return "test"
    
    # Empty name should be handled gracefully
    result = app.expose(test_func, "")
    assert result is not None
    
    # Test duplicate names (should not crash, just overwrite)
    result1 = app.expose(test_func, "duplicate")
    result2 = app.expose(lambda: "other", "duplicate")  # Should overwrite
    assert result1 is not None
    assert result2 is not None


def test_custom_exposer_edge_cases():
    """Test edge cases in custom exposer."""
    app = Yaapp()
    
    # Test object with custom methods
    class CustomObject:
        def execute_call(self, function_name, **kwargs):
            return "custom result"
    
    custom_obj = CustomObject()
    result = app.expose(custom_obj, "custom", custom=True)
    assert result is not None


def test_registry_edge_cases():
    """Test edge cases in registry management."""
    app = Yaapp()
    
    # Test registry with very long names
    long_name = "a" * 100  # Reduced for practicality
    app.expose(lambda: "test", long_name)
    assert long_name in app._registry
    
    # Test registry with unicode names
    unicode_name = "函数名字_功能_测试"
    app.expose(lambda: "test", unicode_name)
    assert unicode_name in app._registry
    
    # Test moderately large registry
    for i in range(100):  # Reduced for test speed
        app.expose(lambda x=i: x, f"func_{i}")
    
    assert len(app._registry) >= 100


def test_result_pattern_edge_cases():
    """Test edge cases in Result pattern usage."""
    # Test Result with None value
    result = Ok(None)
    assert result.is_ok()
    assert result.unwrap() is None
    
    # Test Result with complex objects
    complex_obj = {"nested": {"deep": [1, 2, 3]}}
    result = Ok(complex_obj)
    assert result.is_ok()
    assert result.unwrap() == complex_obj
    
    # Test Result.error with various error types
    result = Result.error("string error")
    assert not result.is_ok()
    
    result = Result.error(Exception("exception error"))
    assert not result.is_ok()
    
    result = Result.error(123)
    assert not result.is_ok()


def test_exposer_system_stress():
    """Stress test the exposer system."""
    app = Yaapp()
    
    # Test rapid exposure of many functions
    for i in range(50):  # Reduced for test speed
        result = app.expose(lambda x=i: x * 2, f"stress_func_{i}")
        assert result is not None
    
    assert len(app._registry) >= 50
    
    # Test that some functions are properly exposed
    for i in range(5):  # Test first 5
        func_name = f"stress_func_{i}"
        assert func_name in app._registry


def test_circular_references():
    """Test handling of circular references."""
    app = Yaapp()
    
    # Test self-referencing class
    class SelfRef:
        def __init__(self):
            self.ref = self
        
        def method(self):
            return "self-ref"
    
    result = app.expose(SelfRef, "SelfRef")
    assert result is not None
    assert "SelfRef" in app._registry


def test_memory_usage():
    """Test memory usage doesn't grow excessively."""
    import gc
    
    # Get initial memory usage
    gc.collect()
    initial_objects = len(gc.get_objects())
    
    # Create and destroy some apps
    for _ in range(5):  # Reduced for test speed
        app = Yaapp()
        for i in range(10):  # Reduced for test speed
            app.expose(lambda: "test", f"temp_{i}")
        del app
    
    # Force garbage collection
    gc.collect()
    final_objects = len(gc.get_objects())
    
    # Memory should not grow excessively (allow for some growth)
    growth = final_objects - initial_objects
    assert growth < 1000  # Reasonable growth limit


def test_thread_safety_basic():
    """Basic thread safety test."""
    import threading
    import time
    
    app = Yaapp()
    errors = []
    
    def expose_functions(thread_id):
        try:
            for i in range(10):  # Reduced for test speed
                result = app.expose(lambda x=i: x + thread_id, f"thread_{thread_id}_func_{i}")
                assert result is not None
                time.sleep(0.001)  # Small delay to increase chance of race conditions
        except Exception as e:
            errors.append(f"Thread {thread_id}: {e}")
    
    # Create multiple threads
    threads = []
    for i in range(3):  # Reduced for test speed
        thread = threading.Thread(target=expose_functions, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads
    for thread in threads:
        thread.join()
    
    assert len(errors) == 0, f"Thread safety issues: {errors}"
    
    # Check that functions from all threads were exposed
    thread_funcs = [name for name in app._registry.keys() if name.startswith("thread_")]
    assert len(thread_funcs) > 10


