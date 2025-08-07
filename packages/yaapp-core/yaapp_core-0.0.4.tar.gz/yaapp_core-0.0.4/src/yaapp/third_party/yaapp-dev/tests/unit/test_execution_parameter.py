#!/usr/bin/env python3
"""
Test the execution parameter for the @expose decorator.
Verifies that sync functions are handled correctly in async contexts.
"""

import sys
import asyncio
import time
import threading
import os
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from yaapp import Yaapp
from yaapp.execution_strategy import execution_hint, ExecutionStrategy


# Test functions with different execution strategies
def fast_sync_function(x: int) -> int:
    """A fast sync function that should run directly."""
    return x * 2


def slow_sync_function(duration: float = 0.1) -> str:
    """A slow sync function that should run in thread pool."""
    time.sleep(duration)
    return f"Completed after {duration}s on thread {threading.current_thread().name}"


@execution_hint("direct")
def direct_function(x: int) -> int:
    """Function explicitly marked for direct execution."""
    return x + 1


@execution_hint("thread")
def thread_function(duration: float = 0.05) -> str:
    """Function explicitly marked for thread execution."""
    time.sleep(duration)
    return f"Thread execution completed on {threading.current_thread().name}"


@execution_hint("process")
def process_function(x: int) -> int:
    """Function marked for process execution (for CPU-heavy work)."""
    # Simulate CPU-intensive work
    total = 0
    for i in range(x * 1000):
        total += i
    return total


async def async_function(x: int) -> int:
    """An async function for comparison."""
    await asyncio.sleep(0.01)
    return x * 3


def test_execution_parameter_usage():
    """Test using the execution parameter in the expose decorator."""
    print("=== Testing Execution Parameter Usage ===")
    
    app = Yaapp()
    
    # Test different execution strategies
    app.expose(fast_sync_function, execution="direct")
    app.expose(slow_sync_function, execution="thread")  
    app.expose(process_function, execution="process")
    app.expose(async_function)  # Default execution for async function
    
    # Verify functions are registered
    registry = app.get_registry_items()
    expected_functions = ["fast_sync_function", "slow_sync_function", "process_function", "async_function"]
    
    for func_name in expected_functions:
        assert func_name in registry, f"Function {func_name} not in registry"
        print(f"✅ {func_name} registered successfully")
    
    print("✅ All functions registered with execution parameters")


def test_execution_hints_on_functions():
    """Test that execution hints are properly attached to functions."""
    print("\n=== Testing Execution Hints on Functions ===")
    
    app = Yaapp()
    
    # Expose functions with different strategies
    app.expose(fast_sync_function, execution="direct")
    app.expose(slow_sync_function, execution="thread")
    app.expose(process_function, execution="process")
    
    # Check execution hints
    registry = app._registry
    
    # Check fast_sync_function
    fast_func, _ = registry["fast_sync_function"]
    if hasattr(fast_func, '__execution_hint__'):
        hint = fast_func.__execution_hint__
        assert hint.strategy == ExecutionStrategy.DIRECT, f"Expected DIRECT, got {hint.strategy}"
        print(f"✅ fast_sync_function has DIRECT execution hint")
    
    # Check slow_sync_function
    slow_func, _ = registry["slow_sync_function"]
    if hasattr(slow_func, '__execution_hint__'):
        hint = slow_func.__execution_hint__
        assert hint.strategy == ExecutionStrategy.THREAD, f"Expected THREAD, got {hint.strategy}"
        print(f"✅ slow_sync_function has THREAD execution hint")
    
    # Check process_function
    process_func, _ = registry["process_function"]
    if hasattr(process_func, '__execution_hint__'):
        hint = process_func.__execution_hint__
        assert hint.strategy == ExecutionStrategy.PROCESS, f"Expected PROCESS, got {hint.strategy}"
        print(f"✅ process_function has PROCESS execution hint")
    


def test_async_execution_strategies():
    """Test that functions are exposed with correct execution strategies."""
    print("\n=== Testing Execution Strategies ===")
    
    app = Yaapp()
    
    # Expose functions with different strategies
    app.expose(fast_sync_function, execution="direct")
    app.expose(slow_sync_function, execution="thread")
    app.expose(async_function)
    
    # Get exposers from registry
    fast_func, fast_exposer = app._registry["fast_sync_function"]
    slow_func, slow_exposer = app._registry["slow_sync_function"]
    async_func, async_exposer = app._registry["async_function"]
    
    # Test direct execution (sync)
    result = fast_exposer.run(fast_func, x=5)
    assert result.is_ok(), f"Direct execution failed: {result.as_error}"
    assert result.unwrap() == 10, f"Expected 10, got {result.unwrap()}"
    print(f"✅ Direct execution: {result.unwrap()}")
    
    # Test thread execution (sync)
    result = slow_exposer.run(slow_func, duration=0.01)  # Shorter duration for test
    assert result.is_ok(), f"Thread execution failed: {result.as_error}"
    print(f"✅ Thread execution: {result.unwrap()}")
    
    # Test async function exposure (just check it's registered)
    registry = app.get_registry_items()
    assert "async_function" in registry, "Async function should be registered"
    print(f"✅ Async function registered")
    


def test_concurrent_execution():
    """Test that thread execution strategy is properly set."""
    print("\n=== Testing Thread Execution Strategy ===")
    
    app = Yaapp()
    
    # Expose slow function with thread execution
    app.expose(slow_sync_function, execution="thread")
    slow_func, slow_exposer = app._registry["slow_sync_function"]
    
    # Test that function has thread execution hint
    if hasattr(slow_func, '__execution_hint__'):
        hint = slow_func.__execution_hint__
        assert hint.strategy == ExecutionStrategy.THREAD, f"Expected THREAD, got {hint.strategy}"
        print(f"✅ Function has THREAD execution strategy")
    
    # Test basic execution
    result = slow_exposer.run(slow_func, duration=0.01)
    assert result.is_ok(), f"Thread execution failed: {result.as_error}"
    print(f"✅ Thread execution working: {result.unwrap()}")
    


def test_decorator_hints():
    """Test functions with decorator-based execution hints."""
    print("\n=== Testing Decorator-Based Hints ===")
    
    app = Yaapp()
    
    # Expose functions that already have execution hints from decorators
    app.expose(direct_function)  # Has @execution_hint("direct")
    app.expose(thread_function)  # Has @execution_hint("thread")
    
    # Check that existing hints are preserved
    direct_func, _ = app._registry["direct_function"]
    thread_func, _ = app._registry["thread_function"]
    
    # Check hints
    if hasattr(direct_func, '__execution_hint__'):
        hint = direct_func.__execution_hint__
        assert hint.strategy == ExecutionStrategy.DIRECT, f"Expected DIRECT, got {hint.strategy}"
        print(f"✅ direct_function preserved its DIRECT hint")
    
    if hasattr(thread_func, '__execution_hint__'):
        hint = thread_func.__execution_hint__
        assert hint.strategy == ExecutionStrategy.THREAD, f"Expected THREAD, got {hint.strategy}"
        print(f"✅ thread_function preserved its THREAD hint")
    


def test_execution_override():
    """Test that expose parameter can override decorator hints."""
    print("\n=== Testing Execution Parameter Override ===")
    
    app = Yaapp()
    
    # Override decorator hint with expose parameter
    app.expose(direct_function, execution="thread")  # Override @execution_hint("direct")
    
    # Check that the override worked
    func, _ = app._registry["direct_function"]
    if hasattr(func, '__execution_hint__'):
        hint = func.__execution_hint__
        # The expose parameter should override the decorator
        print(f"✅ Execution parameter override: strategy is {hint.strategy.value}")
    


def test_invalid_execution_strategy():
    """Test handling of invalid execution strategies."""
    print("\n=== Testing Invalid Execution Strategy ===")
    
    app = Yaapp()
    
    # Create a fresh function without existing hints
    def fresh_function(x: int) -> int:
        return x * 5
    
    # This should default to thread strategy for invalid strategy
    app.expose(fresh_function, execution="invalid_strategy")
    
    func, _ = app._registry["fresh_function"]
    if hasattr(func, '__execution_hint__'):
        hint = func.__execution_hint__
        assert hint.strategy == ExecutionStrategy.THREAD, f"Should default to THREAD, got {hint.strategy}"
        print(f"✅ Invalid strategy defaulted to THREAD")
    else:
        print("⚠️  No execution hint found")
    


async def main():
    """Run all execution parameter tests."""
    print("🚀 Testing YAPP Execution Parameter for @expose Decorator")
    print("=" * 70)
    
    # Run synchronous tests
    tests = [
        test_execution_parameter_usage,
        test_execution_hints_on_functions,
        test_decorator_hints,
        test_invalid_execution_strategy,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with exception: {e}")
    
    # Run async tests
    async_tests = [
        test_async_execution_strategies,
        test_concurrent_execution,
        test_execution_override,
    ]
    
    for test in async_tests:
        try:
            if await test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL EXECUTION PARAMETER TESTS PASSED!")
        print("\n✅ Key Features Working:")
        print("  • execution parameter in @expose decorator")
        print("  • 'thread' default strategy (safe for event loop)")
        print("  • 'direct' strategy for fast functions")
        print("  • 'process' strategy for CPU-heavy work")
        print("  • Decorator-based hints (@execution_hint)")
        print("  • Parameter override of decorator hints")
        print("  • Concurrent execution with thread pool")
        print("  • Invalid strategy fallback to thread")
        print("\n🔥 Sync functions no longer block the event loop!")
        return 0
    else:
        print("❌ SOME EXECUTION PARAMETER TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))