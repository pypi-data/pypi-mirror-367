#!/usr/bin/env python3
"""
Comprehensive server mode tests for YAPP framework.
Tests FastAPI server functionality, API endpoints, and integration.
"""

import sys
import threading
import time
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    requests = None
import subprocess
import signal
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, "../../src")

from yaapp import Yaapp


class ServerTestResults:
    """Track server test results."""
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
        print(f"\n=== SERVER TEST SUMMARY ===")
        print(f"Total: {total}, Passed: {self.passed}, Failed: {self.failed}")
        if self.errors:
            print("\nFAILED TESTS:")
            for error in self.errors:
                print(f"  {error}")
        return self.failed == 0


def test_server_startup_and_endpoints(results):
    """Test server startup and basic API endpoints."""
    print("\n=== Testing Server Startup and Basic Endpoints ===")
    
    # Create test app
    app = Yaapp()
    
    @app.expose
    def test_function(x: int, y: int = 5) -> dict:
        return {"result": x + y, "method": "test"}
    
    @app.expose
    class TestClass:
        def multiply(self, a: int, b: int) -> int:
            return a * b
    
    # Start server in subprocess
    server_process = None
    try:
        # Create temporary test file
        test_file = Path("temp_test_server.py")
        test_file.write_text(f"""
import sys
from yaapp import Yaapp

app = Yaapp()

@app.expose
def test_function(x: int, y: int = 5) -> dict:
    return {{"result": x + y, "method": "test"}}

@app.expose  
class TestClass:
    def multiply(self, a: int, b: int) -> int:
        return a * b

if __name__ == "__main__":
    app.run()
""")
        
        # Start server
        server_process = subprocess.Popen([
            sys.executable, "temp_test_server.py", "server", "--port", "8891"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(0.1)
        
        base_url = "http://localhost:8891"
        
        # Test 1: Health check / root endpoint
        try:
            response = requests.get(f"{base_url}/docs")
            results.assert_true(response.status_code in [200, 404], "Server is responding")
        except Exception as e:
            results.assert_true(False, f"Server health check failed: {e}")
        
        # Test 2: API description endpoint
        try:
            response = requests.get(f"{base_url}/_describe_rpc")
            if response.status_code == 200:
                data = response.json()
                results.assert_true("functions" in data, "API description has functions")
                results.assert_true("test_function" in str(data), "test_function in API description")
            else:
                results.assert_true(False, f"API description failed: {response.status_code}")
        except Exception as e:
            results.assert_true(False, f"API description request failed: {e}")
        
        # Test 3: RPC endpoint - function call
        try:
            response = requests.post(f"{base_url}/_rpc", json={
                "function": "test_function",
                "args": {"x": 10, "y": 3}
            })
            if response.status_code == 200:
                data = response.json()
                results.assert_equal(data.get("result"), 13, "RPC function call result")
                results.assert_equal(data.get("method"), "test", "RPC function call method")
            else:
                results.assert_true(False, f"RPC call failed: {response.status_code}")
        except Exception as e:
            results.assert_true(False, f"RPC call request failed: {e}")
        
        # Test 4: RPC endpoint - class method call  
        try:
            response = requests.post(f"{base_url}/_rpc", json={
                "function": "TestClass.multiply", 
                "args": {"a": 4, "b": 7}
            })
            if response.status_code == 200:
                data = response.json()
                results.assert_equal(data, 28, "RPC class method call result")
            else:
                results.assert_true(False, f"RPC class method call failed: {response.status_code}")
        except Exception as e:
            results.assert_true(False, f"RPC class method call failed: {e}")
        
        # Test 5: Direct function endpoint
        try:
            response = requests.post(f"{base_url}/test_function", json={"x": 20})
            if response.status_code == 200:
                data = response.json()
                results.assert_equal(data.get("result"), 25, "Direct function endpoint result")
            else:
                results.assert_true(False, f"Direct function endpoint failed: {response.status_code}")
        except Exception as e:
            results.assert_true(False, f"Direct function endpoint failed: {e}")
        
        # Test 6: Error handling - invalid function
        try:
            response = requests.post(f"{base_url}/_rpc", json={
                "function": "nonexistent_function",
                "args": {}
            })
            # Check either proper HTTP error status OR error in response body
            has_error = (response.status_code in [400, 404, 422] or 
                        (response.status_code == 200 and "error" in response.json()))
            results.assert_true(has_error, "Invalid function returns error status")
        except Exception as e:
            results.assert_true(False, f"Error handling test failed: {e}")
            
    finally:
        # Cleanup
        if server_process:
            server_process.terminate()
            server_process.wait(timeout=5)
        
        if test_file.exists():
            test_file.unlink()


def test_async_server_functionality(results):
    """Test server with async functions."""
    print("\n=== Testing Async Server Functionality ===")
    
    server_process = None
    try:
        # Create async test file
        test_file = Path("temp_async_server.py")
        test_file.write_text(f"""
import sys
import asyncio
from yaapp import Yaapp

app = Yaapp()

@app.expose
async def async_function(value: int, delay: float = 0.01) -> dict:
    await asyncio.sleep(delay)
    return {{"value": value, "doubled": value * 2, "async": True}}

@app.expose
def sync_function(text: str) -> dict:
    return {{"text": text, "length": len(text), "sync": True}}

if __name__ == "__main__":
    app.run()
""")
        
        # Start server
        server_process = subprocess.Popen([
            sys.executable, "temp_async_server.py", "server", "--port", "8892"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(0.1)
        
        base_url = "http://localhost:8892"
        
        # Test async function via RPC
        try:
            response = requests.post(f"{base_url}/_rpc", json={
                "function": "async_function",
                "args": {"value": 42}
            })
            if response.status_code == 200:
                data = response.json()
                results.assert_equal(data.get("doubled"), 84, "Async function RPC result")
                results.assert_true(data.get("async"), "Async function flag")
            else:
                results.assert_true(False, f"Async RPC call failed: {response.status_code}")
        except Exception as e:
            results.assert_true(False, f"Async RPC call failed: {e}")
        
        # Test sync function via RPC
        try:
            response = requests.post(f"{base_url}/_rpc", json={
                "function": "sync_function", 
                "args": {"text": "hello"}
            })
            if response.status_code == 200:
                data = response.json()
                results.assert_equal(data.get("length"), 5, "Sync function RPC result")
                results.assert_true(data.get("sync"), "Sync function flag")
            else:
                results.assert_true(False, f"Sync RPC call failed: {response.status_code}")
        except Exception as e:
            results.assert_true(False, f"Sync RPC call failed: {e}")
            
    finally:
        # Cleanup
        if server_process:
            server_process.terminate()
            server_process.wait(timeout=5)
        
        if test_file.exists():
            test_file.unlink()


def test_server_with_real_examples(results):
    """Test server mode with actual example apps."""
    print("\n=== Testing Server with Real Example Apps ===")
    
    server_process = None
    try:
        # Test data analyzer example
        server_process = subprocess.Popen([
            sys.executable, "examples/data-analyzer/app.py", "server", "--port", "8893"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=".")
        
        # Wait for server to start
        time.sleep(0.1)
        
        base_url = "http://localhost:8893"
        
        # Test API description
        try:
            response = requests.get(f"{base_url}/_describe_rpc")
            if response.status_code == 200:
                data = response.json()
                results.assert_true("functions" in data, "Data analyzer API has functions")
                functions = str(data)
                results.assert_true("load_csv_file" in functions, "load_csv_file in data analyzer API")
                results.assert_true("analyze_column" in functions, "analyze_column in data analyzer API")
            else:
                results.assert_true(False, f"Data analyzer API description failed: {response.status_code}")
        except Exception as e:
            results.assert_true(False, f"Data analyzer API test failed: {e}")
        
        # Test a specific function call
        try:
            response = requests.post(f"{base_url}/_rpc", json={
                "function": "math.basic_stats",
                "args": {"values": "1,2,3,4,5"}
            })
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "error" not in data:
                    results.assert_true("mean" in data, "Basic stats returns mean")
                    results.assert_equal(data.get("mean"), 3.0, "Basic stats mean calculation")
                else:
                    results.assert_true(False, f"Math function returned error: {data}")
            else:
                results.assert_true(False, f"Math function call failed: {response.status_code}")
        except Exception as e:
            results.assert_true(False, f"Math function call failed: {e}")
            
    finally:
        # Cleanup
        if server_process:
            server_process.terminate()
            server_process.wait(timeout=5)
    
    # Test async example
    server_process = None
    try:
        server_process = subprocess.Popen([
            sys.executable, "examples/data-analyzer/app_async.py", "server", "--port", "8894"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=".")
        
        # Wait for server to start
        time.sleep(0.1)
        
        base_url = "http://localhost:8894"
        
        # Test async function
        try:
            response = requests.post(f"{base_url}/_rpc", json={
                "function": "sync_basic_stats", 
                "args": {"numbers": [10, 20, 30]}
            })
            if response.status_code == 200:
                data = response.json()
                results.assert_equal(data.get("mean"), 20.0, "Async app sync function")
            else:
                results.assert_true(False, f"Async app function call failed: {response.status_code}")
        except Exception as e:
            results.assert_true(False, f"Async app function call failed: {e}")
            
    finally:
        # Cleanup  
        if server_process:
            server_process.terminate()
            server_process.wait(timeout=5)


def main():
    """Run all server tests."""
    if not HAS_REQUESTS:
        print("⚠️  Requests not available - skipping HTTP tests")
        print("✅ Test skipped gracefully")
        return
        
    print("🌐 YAPP Server Mode Tests")
    print("Testing FastAPI server functionality and API endpoints.")
    
    results = ServerTestResults()
    
    # Run all test suites
    test_server_startup_and_endpoints(results)
    test_async_server_functionality(results)
    test_server_with_real_examples(results)
    
    # Show summary
    success = results.summary()
    
    if success:
        print("\n🎉 ALL SERVER TESTS PASSED!")
        print("Server mode is working correctly.")
    else:
        print("\n💥 SERVER TESTS FAILED!")
        print("Issues detected in server functionality.")
        sys.exit(1)


if __name__ == "__main__":
    main()