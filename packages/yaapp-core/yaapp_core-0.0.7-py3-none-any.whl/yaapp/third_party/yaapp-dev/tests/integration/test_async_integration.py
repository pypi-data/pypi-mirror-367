#!/usr/bin/env python3
"""
Comprehensive async integration tests for YAPP framework.
Tests async/sync dual interface functionality end-to-end.
"""

import sys
import asyncio
import tempfile
import json
import csv
from pathlib import Path

# Add src to path
sys.path.insert(0, "../../src")

from yaapp import Yaapp
from yaapp.async_compat import async_compatible


class AsyncTestResults:
    """Track async test results."""
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
        print(f"\n=== ASYNC TEST SUMMARY ===")
        print(f"Total: {total}, Passed: {self.passed}, Failed: {self.failed}")
        if self.errors:
            print("\nFAILED TESTS:")
            for error in self.errors:
                print(f"  {error}")
        return self.failed == 0


def test_async_function_exposure_and_execution(results):
    """Test exposing and executing async functions."""
    print("\n=== Testing Async Function Exposure and Execution ===")
    
    app = Yaapp()
    
    # Define test functions
    @app.expose
    async def async_greet(name: str, delay: float = 0.01) -> str:
        await asyncio.sleep(delay)
        return f"Hello async, {name}!"
    
    @app.expose  
    def sync_greet(name: str) -> str:
        return f"Hello sync, {name}!"
    
    # Test that both are in registry
    results.assert_true('async_greet' in app._registry, "Async function in registry")
    results.assert_true('sync_greet' in app._registry, "Sync function in registry")
    
    # Test async function has sync wrapper
    # Get the function from registry and test sync wrapper
    async_func_result = app.get_registry_item("async_greet")
    if async_func_result.is_ok():
        async_func = async_func_result.unwrap()
        results.assert_true(hasattr(async_func, 'sync'), "Async function has sync wrapper")
        
        # Test sync execution of async function
        result = async_func.sync("Test")
        results.assert_equal(result, "Hello async, Test!", "Async function sync execution")
    else:
        results.assert_true(False, f"Failed to get async function: {async_func_result.as_error}")
        return
    
    # Test async execution
    async def test_async_execution():
        result = await async_func("AsyncTest")
        results.assert_equal(result, "Hello async, AsyncTest!", "Async function async execution")
        
        # Test sync function in async context
        result = await sync_func.async_version("SyncInAsync")
        results.assert_equal(result, "Hello sync, SyncInAsync!", "Sync function in async context")
        
    # Test sync function has async wrapper
    sync_func_result = app.get_registry_item('sync_greet')
    if sync_func_result.is_ok():
        sync_func = sync_func_result.unwrap()
        results.assert_true(hasattr(sync_func, 'async_version'), "Sync function has async wrapper")
    else:
        results.assert_true(False, f"Failed to get sync function: {sync_func_result.as_error}")
        return
    
    asyncio.run(test_async_execution())


def test_async_class_methods(results):
    """Test classes with async methods."""
    print("\n=== Testing Async Class Methods ===")
    
    app = Yaapp()
    
    @app.expose
    class AsyncTestClass:
        async def async_method(self, x: int) -> int:
            await asyncio.sleep(0.01)
            return x * 2
        
        def sync_method(self, x: int) -> int:
            return x * 3
        
        async def slow_computation(self, numbers: list) -> dict:
            await asyncio.sleep(0.02)
            return {
                "sum": sum(numbers),
                "count": len(numbers),
                "avg": sum(numbers) / len(numbers) if numbers else 0
            }
    
    results.assert_true('AsyncTestClass' in app._registry, "Async class in registry")
    
    # Test class instantiation and method calls
    instance = AsyncTestClass()
    
    # Test sync method
    result = instance.sync_method(5)
    results.assert_equal(result, 15, "Sync method execution")
    
    # Test async method in sync context (using sync wrapper)
    async_method = instance.async_method
    if hasattr(async_method, 'sync'):
        result = async_method.sync(7)
        results.assert_equal(result, 14, "Async method sync execution")
    
    # Test async method in async context  
    async def test_async_methods():
        result = await instance.async_method(10)
        results.assert_equal(result, 20, "Async method async execution")
        
        result = await instance.slow_computation([1, 2, 3, 4, 5])
        expected = {"sum": 15, "count": 5, "avg": 3.0}
        results.assert_equal(result, expected, "Complex async method execution")
    
    asyncio.run(test_async_methods())


def test_async_custom_objects(results):
    """Test custom objects with async execute_call."""
    print("\n=== Testing Async Custom Objects ===")
    
    app = Yaapp()
    
    class AsyncCustomProcessor:
        def expose_to_registry(self, name, exposer):
            pass
        
        async def execute_call(self, function_name: str, **kwargs) -> dict:
            if function_name == "process_data":
                data = kwargs.get("data", [])
                await asyncio.sleep(0.01)  # Simulate processing
                return {
                    "processed_items": len(data),
                    "processing_method": "async_custom",
                    "timestamp": "simulated"
                }
            elif function_name == "analyze":
                value = kwargs.get("value", 0)
                await asyncio.sleep(0.005)
                return {
                    "value": value,
                    "doubled": value * 2,
                    "analysis_method": "async_custom"
                }
            else:
                return {"error": f"Unknown function: {function_name}"}
    
    processor = AsyncCustomProcessor()
    app.expose(processor, name="async_processor", custom=True)
    
    results.assert_true('async_processor' in app._registry, "Async custom object in registry")
    
    # Test custom object execution
    # Note: In real usage, this would be called through the framework's execution system
    async def test_custom_execution():
        result = await processor.execute_call("process_data", data=[1, 2, 3, 4])
        expected_items = 4
        results.assert_equal(result["processed_items"], expected_items, "Custom async processing")
        
        result = await processor.execute_call("analyze", value=42)
        results.assert_equal(result["doubled"], 84, "Custom async analysis")
    
    asyncio.run(test_custom_execution())


def test_mixed_sync_async_app(results):
    """Test app with mixed sync and async functions."""
    print("\n=== Testing Mixed Sync/Async App ===")
    
    app = Yaapp()
    
    # Mix of sync and async functions
    @app.expose
    def sync_calculator(x: int, y: int, operation: str = "add") -> int:
        if operation == "add":
            return x + y
        elif operation == "multiply":
            return x * y
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    @app.expose
    async def async_calculator(x: int, y: int, operation: str = "add") -> int:
        # Simulate async computation delay
        await asyncio.sleep(0.01)
        if operation == "add":
            return x + y
        elif operation == "multiply":
            return x * y
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    @app.expose
    class MixedCalculator:
        def sync_divide(self, x: int, y: int) -> float:
            if y == 0:
                raise ValueError("Division by zero")
            return x / y
        
        async def async_power(self, base: int, exponent: int) -> int:
            await asyncio.sleep(0.005)
            return base ** exponent
    
    # Custom async object
    class AsyncMathProcessor:
        def expose_to_registry(self, name, exposer):
            pass
        
        async def execute_call(self, function_name: str, **kwargs) -> dict:
            if function_name == "complex_math":
                numbers = kwargs.get("numbers", [])
                await asyncio.sleep(0.02)
                return {
                    "sum": sum(numbers),
                    "product": eval("*".join(map(str, numbers))) if numbers else 0,
                    "count": len(numbers)
                }
            return {"error": f"Unknown function: {function_name}"}
    
    math_processor = AsyncMathProcessor()
    app.expose(math_processor, name="math_processor", custom=True)
    
    # Test registry contents
    expected_functions = ['sync_calculator', 'async_calculator', 'MixedCalculator', 'math_processor']
    for func_name in expected_functions:
        results.assert_true(func_name in app._registry, f"{func_name} in mixed app registry")
    
    # Test sync function
    sync_calc = app._registry['sync_calculator'][0]
    result = sync_calc(5, 3, "add")
    results.assert_equal(result, 8, "Mixed app sync function")
    
    # Test async function in sync context
    async_calc = app._registry['async_calculator'][0]
    if hasattr(async_calc, 'sync'):
        result = async_calc.sync(5, 3, "multiply")
        results.assert_equal(result, 15, "Mixed app async function in sync context")
    
    # Test async execution
    async def test_mixed_async():
        result = await async_calc(4, 7, "add")
        results.assert_equal(result, 11, "Mixed app async function in async context")
        
        # Test class methods
        calc_instance = MixedCalculator()
        result = calc_instance.sync_divide(10, 2)
        results.assert_equal(result, 5.0, "Mixed app sync method")
        
        result = await calc_instance.async_power(2, 3)
        results.assert_equal(result, 8, "Mixed app async method")
        
        # Test custom processor
        result = await math_processor.execute_call("complex_math", numbers=[2, 3, 4])
        results.assert_equal(result["sum"], 9, "Mixed app custom async processor")
        results.assert_equal(result["product"], 24, "Mixed app custom async product")
    
    asyncio.run(test_mixed_async())


def test_async_error_handling(results):
    """Test error handling in async functions."""
    print("\n=== Testing Async Error Handling ===")
    
    app = Yaapp()
    
    @app.expose
    async def async_function_with_error(should_error: bool = False) -> str:
        await asyncio.sleep(0.01)
        if should_error:
            raise ValueError("Intentional async error")
        return "Success"
    
    @app.expose
    def sync_function_with_error(should_error: bool = False) -> str:
        if should_error:
            raise ValueError("Intentional sync error")
        return "Success"
    
    results.assert_true('async_function_with_error' in app._registry, "Error-prone async function in registry")
    
    # Test successful execution
    # Get function from registry
    async_func_result = app.get_registry_item("async_function_with_error")
    if async_func_result.is_ok():
        async_func = async_func_result.unwrap()
        
        # Test sync wrapper with no error
        if hasattr(async_func, 'sync'):
            result = async_func.sync(should_error=False)
            results.assert_equal(result, "Success", "Async function success in sync context")
        
        # Test sync wrapper with error
        try:
            if hasattr(async_func, 'sync'):
                async_func.sync(should_error=True)
            results.assert_true(False, "Should have raised error in sync context")
        except ValueError as e:
            results.assert_true(str(e) == "Intentional async error", "Correct error in sync context")
    else:
        results.assert_true(False, f"Failed to get async error test function: {async_func_result.as_error}")
    
    # Test async error handling
    async def test_async_errors():
        # Success case
        result = await async_func(should_error=False)
        results.assert_equal(result, "Success", "Async function success in async context")
        
        # Error case
        try:
            await async_func(should_error=True)
            results.assert_true(False, "Should have raised error in async context")
        except ValueError as e:
            results.assert_true(str(e) == "Intentional async error", "Correct error in async context")
    
    asyncio.run(test_async_errors())


def test_async_with_files(results):
    """Test async functionality with actual file I/O."""
    print("\n=== Testing Async with File I/O ===")
    
    app = Yaapp()
    
    @app.expose
    async def async_file_processor(content: str, filename: str = "test.txt") -> dict:
        """Process file content asynchronously."""
        await asyncio.sleep(0.01)  # Simulate I/O delay
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Simulate async file reading
            await asyncio.sleep(0.005)
            with open(temp_path, 'r') as f:
                read_content = f.read()
            
            return {
                "original_length": len(content),
                "read_length": len(read_content),
                "word_count": len(read_content.split()),
                "filename": filename,
                "processing_method": "async"
            }
        finally:
            # Cleanup
            Path(temp_path).unlink()
    
    results.assert_true('async_file_processor' in app._registry, "Async file processor in registry")
    
    # Test file processing
    test_content = "This is a test file with multiple words for async processing."
    
    # Test in sync context
    async_processor = app._registry['async_file_processor'][0]
    if hasattr(async_processor, 'sync'):
        result = async_processor.sync(content=test_content, filename="sync_test.txt")
        results.assert_equal(result["word_count"], 11, "Async file processing in sync context")
        results.assert_equal(result["processing_method"], "async", "Correct processing method")
    
    # Test in async context
    async def test_async_file_processing():
        result = await async_processor(content=test_content, filename="async_test.txt")
        results.assert_equal(result["word_count"], 11, "Async file processing in async context")
        results.assert_equal(result["original_length"], len(test_content), "Correct content length")
    
    asyncio.run(test_async_file_processing())


def test_concurrent_async_operations(results):
    """Test concurrent execution of async operations."""
    print("\n=== Testing Concurrent Async Operations ===")
    
    app = Yaapp()
    
    @app.expose
    async def slow_async_task(task_id: int, delay: float = 0.05) -> dict:
        """Simulate a slow async task."""
        await asyncio.sleep(delay)
        return {
            "task_id": task_id,
            "delay": delay,
            "completed_at": "simulated_timestamp"
        }
    
    results.assert_true('slow_async_task' in app._registry, "Slow async task in registry")
    
    # Test concurrent execution
    async def test_concurrent_execution():
        import time
        
        slow_task = app._registry['slow_async_task'][0]
        
        # Sequential execution (for comparison)
        start_time = time.time()
        result1 = await slow_task(1, delay=0.02)
        result2 = await slow_task(2, delay=0.02) 
        result3 = await slow_task(3, delay=0.02)
        sequential_time = time.time() - start_time
        
        results.assert_equal(result1["task_id"], 1, "Sequential task 1")
        results.assert_equal(result2["task_id"], 2, "Sequential task 2")
        results.assert_equal(result3["task_id"], 3, "Sequential task 3")
        
        # Concurrent execution
        start_time = time.time()
        concurrent_results = await asyncio.gather(
            slow_task(4, delay=0.02),
            slow_task(5, delay=0.02),
            slow_task(6, delay=0.02)
        )
        concurrent_time = time.time() - start_time
        
        # Concurrent should be faster than sequential
        results.assert_true(concurrent_time < sequential_time, "Concurrent execution is faster")
        
        # Check all tasks completed
        for i, result in enumerate(concurrent_results, 4):
            results.assert_equal(result["task_id"], i, f"Concurrent task {i}")
    
    asyncio.run(test_concurrent_execution())


def main():
    """Run all async integration tests."""
    print("🧪 YAPP Async Integration Tests")
    print("Testing async/sync dual interface functionality end-to-end.")
    
    results = AsyncTestResults()
    
    # Run all test suites
    test_async_function_exposure_and_execution(results)
    test_async_class_methods(results) 
    test_async_custom_objects(results)
    test_mixed_sync_async_app(results)
    test_async_error_handling(results)
    test_async_with_files(results)
    test_concurrent_async_operations(results)
    
    # Show summary
    success = results.summary()
    
    if success:
        print("\n🎉 ALL ASYNC INTEGRATION TESTS PASSED!")
        print("The async/sync dual interface is working correctly.")
    else:
        print("\n💥 ASYNC INTEGRATION TESTS FAILED!")  
        print("Issues detected in async/sync functionality.")
        sys.exit(1)


if __name__ == "__main__":
    main()