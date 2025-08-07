#!/usr/bin/env python3
"""
Test async compatibility functionality.
"""

import sys
import asyncio
sys.path.insert(0, "../../src")

from yaapp.async_compat import async_compatible, smart_call, smart_call_async, detect_execution_context


def test_async_compatible_decorator():
    """Test the async_compatible decorator."""
    print("=== Testing async_compatible decorator ===")
    
    # Test with sync function
    @async_compatible
    def sync_func(name: str) -> str:
        return f"Hello, {name}!"
    
    # Should have async wrapper
    assert hasattr(sync_func, 'async_version'), "Sync function should have async wrapper"
    assert not sync_func.is_async, "Sync function should be marked as not async"
    
    # Test sync execution
    result = sync_func("World")
    assert result == "Hello, World!", f"Expected 'Hello, World!', got {result}"
    print("✅ Sync function works")
    
    # Test async wrapper
    async def test_async_wrapper():
        result = await sync_func.async_version("Async")
        assert result == "Hello, Async!", f"Expected 'Hello, Async!', got {result}"
        print("✅ Sync function async wrapper works")
    
    asyncio.run(test_async_wrapper())
    
    # Test with async function
    @async_compatible
    async def async_func(name: str) -> str:
        await asyncio.sleep(0.01)  # Small delay
        return f"Hello async, {name}!"
    
    # Should have sync wrapper
    assert hasattr(async_func, 'sync'), "Async function should have sync wrapper"
    assert async_func.is_async, "Async function should be marked as async"
    
    # Test async execution
    async def test_async_execution():
        result = await async_func("World")
        assert result == "Hello async, World!", f"Expected 'Hello async, World!', got {result}"
        print("✅ Async function works")
    
    asyncio.run(test_async_execution())
    
    # Test sync wrapper
    result = async_func.sync("Sync")
    assert result == "Hello async, Sync!", f"Expected 'Hello async, Sync!', got {result}"
    print("✅ Async function sync wrapper works")


def test_context_detection():
    """Test execution context detection."""
    print("\n=== Testing context detection ===")
    
    # Should be sync context
    context = detect_execution_context()
    assert context == 'sync', f"Expected 'sync' context, got {context}"
    print("✅ Sync context detected correctly")
    
    # Test async context
    async def test_async_context():
        context = detect_execution_context()
        assert context == 'async', f"Expected 'async' context, got {context}"
        print("✅ Async context detected correctly")
    
    asyncio.run(test_async_context())


def test_smart_call_functions():
    """Test smart call functions."""
    print("\n=== Testing smart call functions ===")
    
    @async_compatible
    def sync_test(x: int) -> int:
        return x * 2
    
    @async_compatible
    async def async_test(x: int) -> int:
        await asyncio.sleep(0.01)
        return x * 3
    
    # Test smart_call with sync function
    result = smart_call(sync_test, x=5)
    assert result == 10, f"Expected 10, got {result}"
    print("✅ smart_call with sync function works")
    
    # Test smart_call with async function (should use sync wrapper)
    result = smart_call(async_test, x=5)
    assert result == 15, f"Expected 15, got {result}"
    print("✅ smart_call with async function works")
    
    # Test smart_call_async
    async def test_smart_call_async():
        # With sync function
        result = await smart_call_async(sync_test, x=7)
        assert result == 14, f"Expected 14, got {result}"
        print("✅ smart_call_async with sync function works")
        
        # With async function
        result = await smart_call_async(async_test, x=7)
        assert result == 21, f"Expected 21, got {result}"
        print("✅ smart_call_async with async function works")
    
    asyncio.run(test_smart_call_async())


def main():
    """Run all tests."""
    print("🧪 Testing Async Compatibility Module")
    
    test_async_compatible_decorator()
    test_context_detection()
    test_smart_call_functions()
    
    print("\n🎉 All async compatibility tests passed!")


if __name__ == "__main__":
    main()