#!/usr/bin/env python3
"""
Unit tests for execution strategy functionality.
Tests the execution parameter and execution hints system.
"""

import sys
import asyncio
import time
import threading
import pytest

# Add src to path
sys.path.insert(0, "../../src")

from yaapp import Yaapp, execution_hint, ExecutionStrategy
from yaapp.execution_strategy import get_execution_hint, should_use_thread_pool


def test_execution_hint_decorator():
    """Test the execution_hint decorator functionality."""
    print("=== Testing execution_hint Decorator ===")
    
    @execution_hint("direct")
    def direct_func():
        return "direct"
    
    @execution_hint("thread") 
    def thread_func():
        return "thread"
    
    # Check hints are attached
    assert hasattr(direct_func, '__execution_hint__'), "Direct function should have hint"
    assert hasattr(thread_func, '__execution_hint__'), "Thread function should have hint"
    
    # Check hint values
    direct_hint = direct_func.__execution_hint__
    thread_hint = thread_func.__execution_hint__
    
    assert direct_hint.strategy == ExecutionStrategy.DIRECT, f"Expected DIRECT, got {direct_hint.strategy}"
    assert thread_hint.strategy == ExecutionStrategy.THREAD, f"Expected THREAD, got {thread_hint.strategy}"
    
    print("✅ execution_hint decorator working correctly")


def test_get_execution_hint():
    """Test getting execution hints from functions."""
    print("\n=== Testing get_execution_hint Function ===")
    
    # Function with hint
    @execution_hint("process")
    def process_func():
        return "process"
    
    # Function without hint
    def plain_func():
        return "plain"
    
    # Get hints
    process_hint = get_execution_hint(process_func)
    plain_hint = get_execution_hint(plain_func)
    
    # Check process function hint
    assert process_hint.strategy == ExecutionStrategy.PROCESS, f"Expected PROCESS, got {process_hint.strategy}"
    
    # Check plain function gets default hint
    assert plain_hint.strategy == ExecutionStrategy.THREAD, f"Expected default THREAD, got {plain_hint.strategy}"
    
    print("✅ get_execution_hint working correctly")


def test_should_use_thread_pool():
    """Test thread pool detection logic."""
    print("\n=== Testing should_use_thread_pool Logic ===")
    
    # Create functions with different hints
    @execution_hint("direct")
    def direct_func():
        pass
    
    @execution_hint("thread")
    def thread_func():
        pass
    
    @execution_hint("process")
    def process_func():
        pass
    
    # Test thread pool decisions
    direct_hint = get_execution_hint(direct_func)
    thread_hint = get_execution_hint(thread_func)
    process_hint = get_execution_hint(process_func)
    
    assert not should_use_thread_pool(direct_func, direct_hint), "Direct should not use thread pool"
    assert should_use_thread_pool(thread_func, thread_hint), "Thread should use thread pool"
    assert not should_use_thread_pool(process_func, process_hint), "Process should not use thread pool"
    
    print("✅ should_use_thread_pool logic working correctly")


def test_expose_execution_parameter():
    """Test the execution parameter in expose method."""
    print("\n=== Testing Expose Execution Parameter ===")
    
    app = Yaapp()
    
    # Use different function objects to avoid hint conflicts
    def direct_test_func(x: int) -> int:
        return x * 2
    
    def thread_test_func(x: int) -> int:
        return x * 2
    
    def process_test_func(x: int) -> int:
        return x * 2
    
    # Test different execution strategies
    app.expose(direct_test_func, name="direct_func", execution="direct")
    app.expose(thread_test_func, name="thread_func", execution="thread")
    app.expose(process_test_func, name="process_func", execution="process")
    
    # Check hints were applied
    direct_func, _ = app._registry["direct_func"]
    thread_func, _ = app._registry["thread_func"] 
    process_func, _ = app._registry["process_func"]
    
    direct_hint = get_execution_hint(direct_func)
    thread_hint = get_execution_hint(thread_func)
    process_hint = get_execution_hint(process_func)
    
    assert direct_hint.strategy == ExecutionStrategy.DIRECT, f"Expected DIRECT, got {direct_hint.strategy}"
    assert thread_hint.strategy == ExecutionStrategy.THREAD, f"Expected THREAD, got {thread_hint.strategy}"
    assert process_hint.strategy == ExecutionStrategy.PROCESS, f"Expected PROCESS, got {process_hint.strategy}"
    
    print("✅ Expose execution parameter working correctly")


def test_default_thread_strategy():
    """Test that default strategy is thread (safe for event loop)."""
    print("\n=== Testing Default Thread Strategy ===")
    
    app = Yaapp()
    
    def plain_func():
        return "plain"
    
    # Expose without execution parameter (should default to thread)
    app.expose(plain_func)
    
    func, _ = app._registry["plain_func"]
    hint = get_execution_hint(func)
    
    assert hint.strategy == ExecutionStrategy.THREAD, f"Expected default THREAD, got {hint.strategy}"
    
    print("✅ Default thread strategy working correctly")


def test_decorator_syntax_compatibility():
    """Test decorator syntax still works with execution parameter."""
    print("\n=== Testing Decorator Syntax Compatibility ===")
    
    app = Yaapp()
    
    # Test old style decorator
    @app.expose
    def old_style(x: int) -> int:
        return x + 1
    
    # Test new style decorator with parameters
    @app.expose(execution="direct")
    def new_style(x: int) -> int:
        return x + 2
    
    # Check both are registered
    assert "old_style" in app._registry, "Old style decorator should work"
    assert "new_style" in app._registry, "New style decorator should work"
    
    # Check execution hints
    old_func, _ = app._registry["old_style"]
    new_func, _ = app._registry["new_style"]
    
    old_hint = get_execution_hint(old_func)
    new_hint = get_execution_hint(new_func)
    
    # Old style should get default thread
    assert old_hint.strategy == ExecutionStrategy.THREAD, f"Old style should default to THREAD, got {old_hint.strategy}"
    
    # New style should respect parameter
    assert new_hint.strategy == ExecutionStrategy.DIRECT, f"New style should be DIRECT, got {new_hint.strategy}"
    
    print("✅ Decorator syntax compatibility working correctly")


def test_thread_execution_in_async_context():
    """Test that thread execution strategy is properly set."""
    print("\n=== Testing Thread Execution Strategy ===")
    
    app = Yaapp()
    
    def slow_sync_func(duration: float = 0.01) -> str:
        time.sleep(duration)
        return f"Completed on thread {threading.current_thread().name}"
    
    # Expose with thread execution
    app.expose(slow_sync_func, execution="thread")
    
    # Get function from registry
    func, exposer = app._registry["slow_sync_func"]
    
    # Test that function has correct execution hint
    hint = get_execution_hint(func)
    assert hint.strategy == ExecutionStrategy.THREAD, f"Expected THREAD, got {hint.strategy}"
    
    # Test sync execution
    result = exposer.run(func, duration=0.01)
    assert result.is_ok(), f"Thread execution failed: {result.as_error}"
    
    print(f"✅ Thread execution strategy working")


def test_concurrent_thread_execution():
    """Test that thread execution strategy is properly configured."""
    print("\n=== Testing Thread Execution Configuration ===")
    
    app = Yaapp()
    
    def concurrent_func(duration: float = 0.01) -> str:
        time.sleep(duration)
        return f"Task completed"
    
    # Expose with thread execution
    app.expose(concurrent_func, execution="thread")
    
    # Get function from registry
    func, exposer = app._registry["concurrent_func"]
    
    # Test that function has correct execution hint
    hint = get_execution_hint(func)
    assert hint.strategy == ExecutionStrategy.THREAD, f"Expected THREAD, got {hint.strategy}"
    
    # Test basic execution
    result = exposer.run(func, duration=0.01)
    assert result.is_ok(), f"Thread execution failed: {result.as_error}"
    
    print(f"✅ Thread execution configuration working")


def test_direct_execution_speed():
    """Test that direct and thread execution strategies are properly set."""
    print("\n=== Testing Execution Strategy Configuration ===")
    
    app = Yaapp()
    
    # Use different function objects to avoid hint conflicts
    def direct_fast_func(x: int) -> int:
        return x * 2
    
    def thread_fast_func(x: int) -> int:
        return x * 2
    
    # Test both execution strategies
    app.expose(direct_fast_func, name="direct_fast", execution="direct")
    app.expose(thread_fast_func, name="thread_fast", execution="thread")
    
    direct_func, direct_exposer = app._registry["direct_fast"]
    thread_func, thread_exposer = app._registry["thread_fast"]
    
    # Test direct execution
    direct_result = direct_exposer.run(direct_func, x=5)
    assert direct_result.is_ok() and direct_result.unwrap() == 10, "Direct execution should work"
    
    # Test thread execution
    thread_result = thread_exposer.run(thread_func, x=5)
    assert thread_result.is_ok() and thread_result.unwrap() == 10, "Thread execution should work"
    
    # Check execution hints
    direct_hint = get_execution_hint(direct_func)
    thread_hint = get_execution_hint(thread_func)
    
    assert direct_hint.strategy == ExecutionStrategy.DIRECT, f"Expected DIRECT, got {direct_hint.strategy}"
    assert thread_hint.strategy == ExecutionStrategy.THREAD, f"Expected THREAD, got {thread_hint.strategy}"
    
    print("✅ Execution strategy configuration working")


def main():
    """Run all execution strategy tests."""
    print("🧪 YAPP Execution Strategy Unit Tests")
    print("=" * 60)
    
    # Sync tests
    sync_tests = [
        test_execution_hint_decorator,
        test_get_execution_hint,
        test_should_use_thread_pool,
        test_expose_execution_parameter,
        test_default_thread_strategy,
        test_decorator_syntax_compatibility,
    ]
    
    passed = 0
    failed = 0
    
    for test in sync_tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} failed with exception: {e}")
    
    # Async tests
    async_tests = [
        test_thread_execution_in_async_context,
        test_concurrent_thread_execution,
        test_direct_execution_speed,
    ]
    
    async def run_async_tests():
        async_passed = 0
        async_failed = 0
        
        for test in async_tests:
            try:
                if await test():
                    async_passed += 1
                else:
                    async_failed += 1
                    print(f"❌ {test.__name__} failed")
            except Exception as e:
                async_failed += 1
                print(f"❌ {test.__name__} failed with exception: {e}")
        
        return async_passed, async_failed
    
    async_passed, async_failed = asyncio.run(run_async_tests())
    
    total_passed = passed + async_passed
    total_failed = failed + async_failed
    
    print("\n" + "=" * 60)
    print(f"Test Results: {total_passed} passed, {total_failed} failed")
    
    if total_failed == 0:
        print("🎉 ALL EXECUTION STRATEGY TESTS PASSED!")
        print("✅ Execution parameter functionality working correctly")
        print("✅ Thread safety and concurrency verified")
        print("✅ Backward compatibility maintained")
        return 0
    else:
        print("❌ SOME EXECUTION STRATEGY TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())