#!/usr/bin/env python3
"""
Test that the registry fix works for examples.
"""

import sys
sys.path.insert(0, "../../src")

from yaapp import Yaapp


def test_registry():
    """Test that exposed functions are added to registry."""
    app = Yaapp()
    
    @app.expose
    def test_func(name: str = "World") -> str:
        return f"Hello, {name}!"
    
    # Check that function was added to registry
    assert 'test_func' in app._registry
    assert app._registry['test_func'][0] == test_func
    
    print("✅ Registry test passed")
    
    # Test class exposure
    @app.expose
    class TestClass:
        def method(self, x: int) -> int:
            return x * 2
    
    assert 'TestClass' in app._registry
    assert app._registry['TestClass'][0] == TestClass
    
    print("✅ Class registry test passed")
    
    # Test custom exposure with simple object
    class SimpleCustomObject:
        def execute_call(self, **kwargs):
            return "custom result"
    
    custom_obj = SimpleCustomObject()
    app.expose(custom_obj, name="custom", custom=True)
    
    assert 'custom' in app._registry
    assert app._registry['custom'][0] == custom_obj
    
    print("✅ Custom registry test passed")
    
    print("✅ All registry tests passed!")


if __name__ == "__main__":
    test_registry()