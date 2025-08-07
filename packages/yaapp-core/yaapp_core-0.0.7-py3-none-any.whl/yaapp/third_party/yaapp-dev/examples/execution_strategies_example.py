#!/usr/bin/env python3
"""
Example demonstrating YAPP execution strategies for sync functions in async contexts.

This example shows how to use the execution parameter and decorators to control
how sync functions are executed when called from async contexts, preventing
event loop blocking.
"""

import sys
import asyncio
import time
from pathlib import Path

# Optional import for network example
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from yaapp import Yaapp, execution_hint, direct_execution, thread_execution


def basic_math(x: int, y: int) -> int:
    """A fast computational function - safe to run directly."""
    return x + y


def slow_computation(iterations: int = 100000) -> int:
    """A slow CPU-bound function - should run in thread/process."""
    total = 0
    for i in range(iterations):
        total += i * i
    return total


def network_request(url: str = "https://httpbin.org/delay/1") -> dict:
    """A network I/O function - should run in thread to avoid blocking."""
    if not HAS_REQUESTS:
        return {"error": "requests module not available", "url": url}
    
    try:
        response = requests.get(url, timeout=5)
        return {"status": response.status_code, "url": url}
    except Exception as e:
        return {"error": str(e), "url": url}


def file_operation(filename: str = "/tmp/yapp_test.txt") -> dict:
    """A file I/O function - should run in thread."""
    try:
        # Write some data
        with open(filename, 'w') as f:
            f.write(f"Test data written at {time.time()}\n")
        
        # Read it back
        with open(filename, 'r') as f:
            content = f.read().strip()
        
        return {"success": True, "content": content}
    except Exception as e:
        return {"error": str(e)}


@direct_execution()
def quick_string_operation(text: str) -> str:
    """Decorator-based direct execution for fast operations."""
    return text.upper().replace(" ", "_")


@thread_execution()
def database_simulation(delay: float = 0.5) -> dict:
    """Decorator-based thread execution for I/O operations."""
    time.sleep(delay)  # Simulate database query
    return {
        "query_result": f"Data retrieved after {delay}s delay",
        "timestamp": time.time()
    }


async def async_function(message: str) -> str:
    """An async function for comparison."""
    await asyncio.sleep(0.1)
    return f"Async: {message}"


def demonstrate_execution_strategies():
    """Demonstrate different execution strategies."""
    print("=== YAPP Execution Strategies Demonstration ===\n")
    
    app = Yaapp()
    
    # Register functions with different execution strategies
    print("📝 Registering functions with execution strategies:")
    
    # Fast functions - direct execution (blocks event loop but very fast)
    app.expose(basic_math, execution="direct")
    print("  ✅ basic_math -> direct execution (fast, blocks event loop)")
    
    # CPU-intensive functions - thread execution (non-blocking)
    app.expose(slow_computation, execution="thread")
    print("  ✅ slow_computation -> thread execution (non-blocking)")
    
    # I/O functions - thread execution (non-blocking)
    app.expose(network_request, execution="thread")
    app.expose(file_operation, execution="thread") 
    print("  ✅ network_request, file_operation -> thread execution (non-blocking)")
    
    # Decorator-based execution hints
    app.expose(quick_string_operation)  # Uses @direct_execution()
    app.expose(database_simulation)     # Uses @thread_execution()
    print("  ✅ Functions with decorator hints registered")
    
    # Async function (default handling)
    app.expose(async_function)
    print("  ✅ async_function -> native async execution")
    
    # Process execution for CPU-heavy work
    app.expose(slow_computation, name="cpu_heavy_computation", execution="process")
    print("  ✅ cpu_heavy_computation -> process execution (CPU-intensive)")
    
    print(f"\n📋 Total functions registered: {len(app.get_registry_items())}")
    
    return app


async def test_execution_performance(app: YApp):
    """Test the performance and behavior of different execution strategies."""
    print("\n🏃 Testing Execution Performance:")
    
    # Get functions from registry
    registry = app._registry
    
    # Test direct execution (fast)
    print("\n1. Direct Execution (fast, blocks event loop):")
    basic_math_func, basic_math_exposer = registry["basic_math"]
    
    start = time.time()
    result = await basic_math_exposer.run_async(basic_math_func, x=10, y=20)
    duration = time.time() - start
    
    print(f"   Result: {result.unwrap()}")
    print(f"   Duration: {duration:.6f}s (very fast!)")
    
    # Test thread execution (I/O)
    print("\n2. Thread Execution (I/O operations):")
    file_func, file_exposer = registry["file_operation"]
    
    start = time.time()
    result = await file_exposer.run_async(file_func, filename="/tmp/yapp_demo.txt")
    duration = time.time() - start
    
    print(f"   Result: {result.unwrap()}")
    print(f"   Duration: {duration:.6f}s (non-blocking)")
    
    # Test async function
    print("\n3. Native Async Execution:")
    async_func, async_exposer = registry["async_function"]
    
    start = time.time()
    result = await async_exposer.run_async(async_func, message="Hello World")
    duration = time.time() - start
    
    print(f"   Result: {result.unwrap()}")
    print(f"   Duration: {duration:.6f}s (native async)")


async def test_concurrent_execution(app: YApp):
    """Test that thread execution allows true concurrency."""
    print("\n🔄 Testing Concurrent Execution:")
    
    registry = app._registry
    db_func, db_exposer = registry["database_simulation"]
    
    print("   Running 3 database simulations concurrently (0.3s each)...")
    
    start = time.time()
    
    # Run 3 tasks concurrently
    tasks = [
        db_exposer.run_async(db_func, delay=0.3),
        db_exposer.run_async(db_func, delay=0.3),
        db_exposer.run_async(db_func, delay=0.3)
    ]
    
    results = await asyncio.gather(*tasks)
    total_duration = time.time() - start
    
    print(f"   Total time: {total_duration:.3f}s (should be ~0.3s, not 0.9s)")
    
    if total_duration < 0.5:
        print("   ✅ True concurrency achieved! (thread pool working)")
    else:
        print("   ❌ Sequential execution detected (concurrency failed)")
    
    # Show results
    for i, result in enumerate(results):
        if result.is_ok():
            data = result.unwrap()
            print(f"   Task {i+1}: {data['query_result']}")


async def test_event_loop_health(app: YApp):
    """Test that the event loop stays responsive during sync function execution."""
    print("\n💓 Testing Event Loop Health:")
    
    registry = app._registry
    slow_func, slow_exposer = registry["slow_computation"]
    
    print("   Starting slow computation in thread...")
    print("   Event loop should remain responsive...")
    
    # Start slow computation
    slow_task = asyncio.create_task(
        slow_exposer.run_async(slow_func, iterations=500000)
    )
    
    # Test event loop responsiveness during computation
    responsive_count = 0
    for i in range(5):
        start = time.time()
        await asyncio.sleep(0.1)  # Should complete quickly if event loop is responsive
        duration = time.time() - start
        
        if duration < 0.15:  # Allow some margin
            responsive_count += 1
            print(f"   ✅ Event loop responsive ({duration:.3f}s)")
        else:
            print(f"   ❌ Event loop blocked ({duration:.3f}s)")
    
    # Wait for slow computation to complete
    result = await slow_task
    
    if result.is_ok():
        print(f"   Slow computation result: {result.unwrap()}")
    
    if responsive_count >= 4:
        print("   🎉 Event loop stayed healthy during thread execution!")
    else:
        print("   ⚠️  Event loop experienced some blocking")


def demonstrate_decorator_usage():
    """Show how to use execution strategy decorators."""
    print("\n🎨 Execution Strategy Decorators:\n")
    
    print("```python")
    print("from yaapp import Yaapp, execution_hint, direct_execution, thread_execution")
    print("")
    print("app = Yaapp()")
    print("")
    print("# Method 1: Using execution parameter")
    print("@app.expose(execution='thread')")
    print("def slow_function():")
    print("    time.sleep(1)")
    print("    return 'done'")
    print("")
    print("# Method 2: Using decorator hints")
    print("@direct_execution()  # Fast functions")
    print("def quick_math(x, y):")
    print("    return x + y")
    print("")
    print("@thread_execution()  # I/O or slow functions") 
    print("def database_query():")
    print("    # Database operation")
    print("    return query_result")
    print("")
    print("@execution_hint('process')  # CPU-intensive")
    print("def heavy_computation():")
    print("    # CPU-heavy work")
    print("    return result")
    print("")
    print("# Register with app")
    print("app.expose(quick_math)")
    print("app.expose(database_query)")
    print("app.expose(heavy_computation)")
    print("```")


async def main():
    """Run the execution strategies demonstration."""
    print("🚀 YAPP Execution Strategies Example")
    print("=" * 60)
    
    # Set up the application
    app = demonstrate_execution_strategies()
    
    # Test different aspects
    await test_execution_performance(app)
    await test_concurrent_execution(app)
    await test_event_loop_health(app)
    
    # Show decorator usage
    demonstrate_decorator_usage()
    
    print("\n" + "=" * 60)
    print("🎯 Summary of Execution Strategies:")
    print("")
    print("📍 DIRECT execution:")
    print("   • Use for: Very fast functions (< 1ms)")
    print("   • Behavior: Blocks event loop but minimal impact")
    print("   • Example: Basic math, string operations")
    print("")
    print("🧵 THREAD execution (DEFAULT):")
    print("   • Use for: I/O operations, moderate CPU work")
    print("   • Behavior: Non-blocking, allows concurrency") 
    print("   • Example: File I/O, network requests, database queries")
    print("")
    print("⚙️  PROCESS execution:")
    print("   • Use for: CPU-intensive computations")
    print("   • Behavior: Separate process, true parallelism")
    print("   • Example: Image processing, data analysis")
    print("")
    print("🤖 AUTO execution:")
    print("   • Use for: Automatic detection based on heuristics")
    print("   • Behavior: Framework decides based on function analysis")
    print("   • Example: Functions with unknown performance characteristics")
    print("")
    print("✨ Key Benefits:")
    print("   • No more event loop blocking from sync functions")
    print("   • Better performance through concurrent execution")
    print("   • Developer control over execution strategy")
    print("   • Safe defaults (thread execution)")
    print("")
    print("🎉 YAPP now handles sync/async execution intelligently!")


if __name__ == "__main__":
    if not HAS_REQUESTS:
        print("⚠️  requests not installed - network example will be skipped")
    
    asyncio.run(main())