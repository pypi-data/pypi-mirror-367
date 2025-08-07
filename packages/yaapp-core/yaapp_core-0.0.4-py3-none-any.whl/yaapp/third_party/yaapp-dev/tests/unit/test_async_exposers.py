#!/usr/bin/env python3
"""
Test async-enabled exposers.
"""

import sys
import asyncio
sys.path.insert(0, "../../src")

from yaapp.exposers import FunctionExposer, ClassExposer, ObjectExposer, CustomExposer
from yaapp.result import Result, Ok


def test_function_exposer_async():
    """Test FunctionExposer with async functions."""
    print("=== Testing FunctionExposer with Async ===")
    
    exposer = FunctionExposer()
    
    # Test sync function
    def sync_func(name: str) -> str:
        return f"Hello, {name}!"
    
    result = exposer.expose(sync_func, "sync_test")
    assert result.is_ok(), f"Failed to expose sync function: {result.as_error}"
    print("✅ Sync function exposed")
    
    # Test sync execution
    result = exposer.run(sync_func, name="World")
    assert result.is_ok(), f"Failed to run sync function: {result.as_error}"
    assert result.unwrap() == "Hello, World!", f"Wrong result: {result.unwrap()}"
    print("✅ Sync function executed")
    
    # Test async function
    async def async_func(name: str) -> str:
        await asyncio.sleep(0.01)
        return f"Hello async, {name}!"
    
    result = exposer.expose(async_func, "async_test")
    assert result.is_ok(), f"Failed to expose async function: {result.as_error}"
    print("✅ Async function exposed")
    
    # Test sync execution of async function
    result = exposer.run(async_func, name="World")
    assert result.is_ok(), f"Failed to run async function in sync: {result.as_error}"
    assert result.unwrap() == "Hello async, World!", f"Wrong result: {result.unwrap()}"
    print("✅ Async function executed in sync context")
    
    # Test async execution
    async def test_async_execution():
        result = await exposer.run_async(async_func, name="Async")
        assert result.is_ok(), f"Failed to run async function: {result.as_error}"
        assert result.unwrap() == "Hello async, Async!", f"Wrong result: {result.unwrap()}"
        print("✅ Async function executed in async context")
        
        # Test sync function in async context
        result = await exposer.run_async(sync_func, name="Sync")
        assert result.is_ok(), f"Failed to run sync function in async: {result.as_error}"
        assert result.unwrap() == "Hello, Sync!", f"Wrong result: {result.unwrap()}"
        print("✅ Sync function executed in async context")
    
    asyncio.run(test_async_execution())


def test_class_exposer_async():
    """Test ClassExposer with async methods."""
    print("\n=== Testing ClassExposer with Async ===")
    
    class TestClass:
        def sync_method(self, x: int) -> int:
            return x * 2
        
        async def async_method(self, x: int) -> int:
            await asyncio.sleep(0.01)
            return x * 3
    
    exposer = ClassExposer()
    
    # Expose the class
    result = exposer.expose(TestClass, "test_class")
    assert result.is_ok(), f"Failed to expose class: {result.as_error}"
    print("✅ Class with async methods exposed")
    
    # Create instance for testing
    instance = TestClass()
    
    # Test sync method
    result = exposer.run(instance.sync_method, x=5)
    assert result.is_ok(), f"Failed to run sync method: {result.as_error}"
    assert result.unwrap() == 10, f"Wrong result: {result.unwrap()}"
    print("✅ Sync method executed")
    
    # Test async method in sync context
    result = exposer.run(instance.async_method, x=5)
    assert result.is_ok(), f"Failed to run async method in sync: {result.as_error}"
    assert result.unwrap() == 15, f"Wrong result: {result.unwrap()}"
    print("✅ Async method executed in sync context")
    
    # Test async execution
    async def test_async_execution():
        result = await exposer.run_async(instance.async_method, x=7)
        assert result.is_ok(), f"Failed to run async method: {result.as_error}"
        assert result.unwrap() == 21, f"Wrong result: {result.unwrap()}"
        print("✅ Async method executed in async context")
    
    asyncio.run(test_async_execution())


def test_custom_exposer_async():
    """Test CustomExposer with async execute_call."""
    print("\n=== Testing CustomExposer with Async ===")
    
    class SyncCustom:
        def expose_to_registry(self, name, exposer):
            pass
        
        def execute_call(self, **kwargs):
            return f"Sync custom: {kwargs.get('message', 'default')}"
    
    class AsyncCustom:
        def expose_to_registry(self, name, exposer):
            pass
        
        async def execute_call(self, **kwargs):
            await asyncio.sleep(0.01)
            return f"Async custom: {kwargs.get('message', 'default')}"
    
    exposer = CustomExposer()
    
    # Test sync custom object
    sync_obj = SyncCustom()
    result = exposer.expose(sync_obj, "sync_custom")
    assert result.is_ok(), f"Failed to expose sync custom: {result.as_error}"
    print("✅ Sync custom object exposed")
    
    result = exposer.run(sync_obj, message="test")
    assert result.is_ok(), f"Failed to run sync custom: {result.as_error}"
    assert result.unwrap() == "Sync custom: test", f"Wrong result: {result.unwrap()}"
    print("✅ Sync custom object executed")
    
    # Test async custom object
    async_obj = AsyncCustom()
    result = exposer.expose(async_obj, "async_custom")
    assert result.is_ok(), f"Failed to expose async custom: {result.as_error}"
    print("✅ Async custom object exposed")
    
    result = exposer.run(async_obj, message="sync_test")
    assert result.is_ok(), f"Failed to run async custom in sync: {result.as_error}"
    assert result.unwrap() == "Async custom: sync_test", f"Wrong result: {result.unwrap()}"
    print("✅ Async custom object executed in sync context")
    
    # Test async execution
    async def test_async_execution():
        result = await exposer.run_async(async_obj, message="async_test")
        assert result.is_ok(), f"Failed to run async custom: {result.as_error}"
        assert result.unwrap() == "Async custom: async_test", f"Wrong result: {result.unwrap()}"
        print("✅ Async custom object executed in async context")
    
    asyncio.run(test_async_execution())


def main():
    """Run all exposer async tests."""
    print("🧪 Testing Async-Enabled Exposers")
    
    test_function_exposer_async()
    test_class_exposer_async()
    test_custom_exposer_async()
    
    print("\n🎉 All async exposer tests passed!")


if __name__ == "__main__":
    main()