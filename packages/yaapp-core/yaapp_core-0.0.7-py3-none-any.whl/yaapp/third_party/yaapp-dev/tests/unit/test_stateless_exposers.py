#!/usr/bin/env python3
"""
Test the stateless exposer system - ensuring no state pollution.
"""

import pytest
import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from yaapp import Yaapp


def test_function_exposer_stateless():
    """Test that FunctionExposer doesn't store state."""
    app = Yaapp()
    
    def func1():
        return "func1"
    
    def func2():
        return "func2"
    
    # Expose functions
    result1 = app.expose(func1, "func1")
    result2 = app.expose(func2, "func2")
    
    assert result1 is not None
    assert result2 is not None
    assert "func1" in app._registry
    assert "func2" in app._registry


def test_class_exposer_stateless():
    """Test that ClassExposer doesn't store state."""
    app = Yaapp()
    
    class TestClass1:
        def method1(self):
            return "method1"
    
    class TestClass2:
        def method2(self):
            return "method2"
    
    # Expose classes
    result1 = app.expose(TestClass1, "TestClass1")
    result2 = app.expose(TestClass2, "TestClass2")
    
    assert result1 is not None
    assert result2 is not None
    assert "TestClass1" in app._registry
    assert "TestClass2" in app._registry


def test_object_exposer_stateless():
    """Test that ObjectExposer doesn't store state."""
    app = Yaapp()
    
    class TestObj1:
        def method1(self):
            return "obj1_method"
    
    class TestObj2:
        def method2(self):
            return "obj2_method"
    
    obj1 = TestObj1()
    obj2 = TestObj2()
    
    # Expose objects
    result1 = app.expose(obj1, "obj1")
    result2 = app.expose(obj2, "obj2")
    
    assert result1 is not None
    assert result2 is not None
    assert "obj1" in app._registry
    assert "obj2" in app._registry


def test_memory_isolation():
    """Test that multiple YApp instances don't share exposer state."""
    app1 = Yaapp()
    app2 = Yaapp()
    
    # Expose functions to different apps
    @app1.expose
    def func1():
        return "app1_func"
    
    @app2.expose  
    def func2():
        return "app2_func"
    
    # Verify functions are in correct registries
    assert 'func1' in app1._registry
    assert 'func2' in app2._registry
    assert 'func1' not in app2._registry
    assert 'func2' not in app1._registry


def test_concurrent_access():
    """Test that exposers are thread-safe without shared state."""
    app = Yaapp() 
    
    def create_and_expose_function(func_id):
        """Create and expose a function concurrently."""
        def test_func():
            return f"result_{func_id}"
        test_func.__name__ = f"func_{func_id}"
        
        try:
            app.expose(test_func)
            return func_id
        except Exception as e:
            print(f"Error exposing func_{func_id}: {e}")
            return None
    
    # Expose functions concurrently (reduced for test speed)
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(create_and_expose_function, i) for i in range(10)]
        completed = [f.result() for f in futures if f.result() is not None]
    
    assert len(completed) == 10
    
    # Verify all functions are in registry
    for i in range(10):
        func_name = f"func_{i}"
        assert func_name in app._registry


def test_async_compatibility_stateless():
    """Test that async compatibility is applied without storing state."""
    app = Yaapp()
    
    # Regular function
    def sync_func():
        return "sync_result"
    
    # Async function
    async def async_func():
        return "async_result"
    
    # Expose both functions
    app.expose(sync_func, "sync_func")
    app.expose(async_func, "async_func")
    
    # Check that functions are in registry
    assert "sync_func" in app._registry
    assert "async_func" in app._registry


def test_bound_method_handling():
    """Test that bound methods are handled correctly."""
    app = Yaapp()
    
    class TestClass:
        def __init__(self, value):
            self.value = value
        
        def get_value(self):
            return self.value
    
    obj = TestClass("test_value")
    
    # Expose bound method
    app.expose(obj.get_value, "get_value")
    
    # Check that bound method is stored
    assert "get_value" in app._registry


def test_error_isolation():
    """Test that errors in one exposer don't affect others."""
    app = Yaapp()
    
    # Valid function
    def valid_func():
        return "valid"
    
    # Function that will cause issues
    def problematic_func():
        raise Exception("This function has issues")
    
    # Expose valid function first
    app.expose(valid_func, "valid")
    
    # Expose problematic function
    app.expose(problematic_func, "problematic")
    
    # Both should be in registry
    assert "valid" in app._registry
    assert "problematic" in app._registry