#!/usr/bin/env python3
"""
Test YaappCore with async support.
"""

import sys
import asyncio
sys.path.insert(0, "../../src")

from yaapp import Yaapp


def test_async_function_exposure():
    """Test that YApp can expose async functions."""
    print("=== Testing YApp Async Function Exposure ===")
    
    app = Yaapp()
    
    # Test sync function
    @app.expose
    def sync_greet(name: str) -> str:
        return f"Hello, {name}!"
    
    # Test async function  
    @app.expose
    async def async_greet(name: str) -> str:
        await asyncio.sleep(0.01)
        return f"Hello async, {name}!"
    
    # Check that both are in registry
    assert 'sync_greet' in app._registry, "Sync function not in registry"
    assert 'async_greet' in app._registry, "Async function not in registry"
    print("✅ Both sync and async functions exposed to registry")
    
    # Check that async function has sync wrapper
    async_func = app._registry['async_greet'][0]
    assert hasattr(async_func, 'sync'), "Async function should have sync wrapper"
    assert async_func.is_async, "Async function should be marked as async"
    print("✅ Async function has sync wrapper")
    
    # Check that sync function has async wrapper
    sync_func = app._registry['sync_greet'][0]
    assert hasattr(sync_func, 'async_version'), "Sync function should have async wrapper"
    assert not sync_func.is_async, "Sync function should be marked as not async"
    print("✅ Sync function has async wrapper")


def test_async_class_exposure():
    """Test that YApp can expose classes with async methods."""
    print("\n=== Testing YApp Async Class Exposure ===")
    
    app = Yaapp()
    
    @app.expose
    class AsyncTestClass:
        def sync_method(self, x: int) -> int:
            return x * 2
        
        async def async_method(self, x: int) -> int:
            await asyncio.sleep(0.01)
            return x * 3
    
    assert 'AsyncTestClass' in app._registry, "Class not in registry"
    print("✅ Class with async methods exposed")


def test_async_custom_exposure():
    """Test that YApp can expose custom objects with async execute_call."""
    print("\n=== Testing YApp Async Custom Exposure ===")
    
    app = Yaapp()
    
    class AsyncCustomObject:
        def expose_to_registry(self, name, exposer):
            pass
        
        async def execute_call(self, **kwargs):
            await asyncio.sleep(0.01)
            return f"Custom async result: {kwargs.get('message', 'default')}"
    
    custom_obj = AsyncCustomObject()
    app.expose(custom_obj, name="async_custom", custom=True)
    
    assert 'async_custom' in app._registry, "Custom object not in registry"
    print("✅ Custom object with async execute_call exposed")


def test_mixed_exposure():
    """Test mixed sync/async exposure in one app."""
    print("\n=== Testing Mixed Sync/Async Exposure ===")
    
    app = Yaapp()
    
    @app.expose
    def sync_func(msg: str) -> str:
        return f"Sync: {msg}"
    
    @app.expose
    async def async_func(msg: str) -> str:
        await asyncio.sleep(0.01)
        return f"Async: {msg}"
    
    @app.expose
    class MixedClass:
        def sync_method(self, x: int) -> int:
            return x + 1
        
        async def async_method(self, x: int) -> int:
            await asyncio.sleep(0.01)
            return x + 2
    
    class MixedCustom:
        def expose_to_registry(self, name, exposer):
            pass
        
        async def execute_call(self, **kwargs):
            await asyncio.sleep(0.01)
            return f"Mixed custom: {kwargs.get('value', 0)}"
    
    mixed_custom = MixedCustom()
    app.expose(mixed_custom, name="mixed_custom", custom=True)
    
    # Check all are registered
    expected_items = ['sync_func', 'async_func', 'MixedClass', 'mixed_custom']
    for item in expected_items:
        assert item in app._registry, f"{item} not in registry"
    
    print(f"✅ Mixed exposure successful. Registry has: {list(app._registry.keys())}")


def main():
    """Run all YaappCore async tests."""
    print("🧪 Testing YaappCore Async Support")
    
    test_async_function_exposure()
    test_async_class_exposure()
    test_async_custom_exposure()
    test_mixed_exposure()
    
    print("\n🎉 All YaappCore async tests passed!")


if __name__ == "__main__":
    main()