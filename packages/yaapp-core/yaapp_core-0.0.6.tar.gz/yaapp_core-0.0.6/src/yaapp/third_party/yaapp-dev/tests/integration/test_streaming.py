#!/usr/bin/env python3
"""
Comprehensive streaming tests for yaapp framework.
Tests SSE (Server-Sent Events) functionality, streaming detection, and client integration.
"""

import sys
import threading
import time
import subprocess
import asyncio
import json
from pathlib import Path
from typing import AsyncGenerator, List, Dict, Any

# Add src to path
sys.path.insert(0, "../../src")

from yaapp import Yaapp


class StreamingTestResults:
    """Track streaming test results."""
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
        print(f"\n=== STREAMING TEST SUMMARY ===")
        print(f"Total: {total}, Passed: {self.passed}, Failed: {self.failed}")
        if self.errors:
            print("\nFAILED TESTS:")
            for error in self.errors:
                print(f"  {error}")
        return self.failed == 0


def test_streaming_detection(results):
    """Test automatic streaming function detection."""
    print("\n=== Testing Streaming Detection ===")
    
    try:
        from yaapp.streaming import StreamDetector
        detector = StreamDetector()
        
        # Test 1: Async generator function should be detected
        async def async_generator_func():
            yield {"data": "test"}
        
        is_streaming = detector.should_stream(async_generator_func)
        results.assert_true(is_streaming, "Async generator function detected as streaming")
        
        # Test 2: Regular function should NOT be detected
        def regular_func():
            return {"data": "test"}
        
        is_streaming = detector.should_stream(regular_func)
        results.assert_true(not is_streaming, "Regular function NOT detected as streaming")
        
        # Test 3: Sync generator function should be detected
        def sync_generator_func():
            yield {"data": "test"}
        
        is_streaming = detector.should_stream(sync_generator_func)
        results.assert_true(is_streaming, "Sync generator function detected as streaming")
        
        # Test 4: Function with stream annotation should be detected
        def annotated_func() -> AsyncGenerator[Dict[str, Any], None]:
            pass
        
        is_streaming = detector.should_stream(annotated_func)
        results.assert_true(is_streaming, "Function with AsyncGenerator annotation detected as streaming")
        
        print("✅ Stream detection tests completed")
        
    except ImportError as e:
        results.assert_true(False, f"StreamDetector import failed: {e}")
    except Exception as e:
        results.assert_true(False, f"Stream detection test failed: {e}")


def test_sse_server_endpoints(results):
    """Test SSE endpoints are properly created by FastAPI runner."""
    print("\n=== Testing SSE Server Endpoints ===")
    
    server_process = None
    try:
        # Create test streaming server
        test_file = Path("temp_streaming_server.py")
        test_file.write_text("""
import sys
import asyncio
import time
from pathlib import Path

# Add src to path for development  
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from yaapp import Yaapp

app = Yaapp()

@app.expose
async def stream_counter(count: int = 3):
    '''Stream counter from 0 to count.'''
    for i in range(count + 1):
        yield {"number": i, "timestamp": time.time()}
        await asyncio.sleep(0.1)

@app.expose
def regular_function(message: str = "hello"):
    '''Regular non-streaming function.'''
    return {"message": message, "timestamp": time.time()}

if __name__ == "__main__":
    app.run()
""")
        
        # Start server
        server_process = subprocess.Popen([
            sys.executable, "temp_streaming_server.py", "server", "--port", "8895"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(0.1)
        
        # Test with httpx for SSE support
        try:
            import httpx
        except ImportError:
            results.assert_true(False, "httpx required for SSE testing. Install with: pip install httpx")
            return
        
        try:
            
            base_url = "http://localhost:8895"
            
            # Test 1: Regular endpoint should work normally
            with httpx.Client() as client:
                response = client.post(f"{base_url}/regular_function", 
                                     json={"message": "test"})
                if response.status_code == 200:
                    data = response.json()
                    results.assert_equal(data.get("message"), "test", "Regular endpoint works")
                else:
                    results.assert_true(False, f"Regular endpoint failed: {response.status_code}")
            
            # Test 2: Streaming endpoint should exist and return SSE
            with httpx.Client() as client:
                with client.stream("POST", f"{base_url}/stream_counter/stream", json={"count": 2}) as response:
                    if response.status_code == 200:
                        content_type = response.headers.get("content-type", "")
                        # SSE can have different content types (text/plain, text/event-stream, etc.)
                        results.assert_true("text/" in content_type, 
                                          f"SSE endpoint returns text content-type (got: {content_type})")
                        
                        # Read first few SSE events
                        events = []
                        for line in response.iter_lines():
                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])  # Remove "data: " prefix
                                    events.append(data)
                                    if len(events) >= 2:  # Get first 2 events
                                        break
                                except json.JSONDecodeError:
                                    pass
                        
                        results.assert_true(len(events) >= 2, "SSE stream produces events")
                        if events:
                            results.assert_true("number" in events[0], "SSE events have expected data structure")
                            results.assert_equal(events[0]["number"], 0, "First SSE event has correct counter value")
                    else:
                        results.assert_true(False, f"SSE endpoint failed: {response.status_code}")
            
        except ImportError:
            results.assert_true(False, "httpx required for SSE testing. Install with: pip install httpx")
        except Exception as e:
            results.assert_true(False, f"SSE endpoint test failed: {e}")
            
    finally:
        # Cleanup
        if server_process:
            server_process.terminate()
            server_process.wait(timeout=5)
        
        if test_file.exists():
            test_file.unlink()


def test_yaapp_client_streaming(results):
    """Test yaapp client with streaming endpoints."""
    print("\n=== Testing YaApp Client Streaming ===")
    
    server_process = None
    try:
        # Create test streaming server
        test_file = Path("temp_client_streaming_server.py")
        test_file.write_text("""
import sys
import asyncio
import time
from pathlib import Path

# Add src to path for development  
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from yaapp import Yaapp

app = Yaapp()

@app.expose
async def simple_stream(items: int = 3):
    '''Simple streaming function for client testing.'''
    for i in range(items):
        yield {"item": i, "message": f"Item {i}"}
        await asyncio.sleep(0.05)  # Short delay for testing

@app.expose
def get_info():
    '''Regular function for client testing.'''
    return {"server": "streaming_test", "version": "1.0"}

if __name__ == "__main__":
    app.run()
""")
        
        # Start server
        server_process = subprocess.Popen([
            sys.executable, "temp_client_streaming_server.py", "server", "--port", "8896"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(0.1)
        
        # Test yaapp client functionality
        try:
            # Add client to path - try multiple possible locations
            client_paths = [
                "../../examples/client",
                "../examples/client", 
                "examples/client"
            ]
            
            YaappStreamingClient = None
            for client_path in client_paths:
                try:
                    sys.path.insert(0, client_path)
                    from client import YaappStreamingClient
                    break
                except ImportError:
                    continue
            
            if YaappStreamingClient is None:
                results.assert_true(False, "YaappStreamingClient not found in any expected location")
                return
            
            client = YaappStreamingClient("http://localhost:8896")
            
            # Test 1: Regular function call
            try:
                result = client.call_function("get_info")
                results.assert_equal(result.get("server"), "streaming_test", "Client regular function call")
            except Exception as e:
                results.assert_true(False, f"Client regular call failed: {e}")
            
            # Test 2: Create streaming test function
            def test_client_streaming():
                """Test client streaming with httpx."""
                try:
                    import httpx
                except ImportError:
                    return False, "httpx required for streaming tests"
                
                import json
                
                url = f"http://localhost:8896/simple_stream/stream"
                events = []
                
                try:
                    with httpx.Client() as http_client:
                        with http_client.stream("POST", url, json={"items": 2}) as response:
                            if response.status_code != 200:
                                return False, f"HTTP {response.status_code}"
                            
                            for line in response.iter_lines():
                                if line.startswith('data: '):
                                    try:
                                        data = json.loads(line[6:])
                                        events.append(data)
                                        if len(events) >= 2:  # Get 2 events
                                            break
                                    except json.JSONDecodeError:
                                        pass
                            
                            return len(events) >= 2, events
                except Exception as e:
                    return False, str(e)
            
            success, data = test_client_streaming()
            results.assert_true(success, "Client can consume SSE streams with httpx")
            
            if success and isinstance(data, list) and len(data) > 0:
                results.assert_true("item" in data[0], "Client receives proper SSE data structure")
                results.assert_equal(data[0]["item"], 0, "Client receives correct SSE event data")
            
        except ImportError as e:
            results.assert_true(False, f"YAppClient import failed: {e}")
        except Exception as e:
            results.assert_true(False, f"Client streaming test failed: {e}")
            
    finally:
        # Cleanup
        if server_process:
            server_process.terminate()
            server_process.wait(timeout=5)
        
        if test_file.exists():
            test_file.unlink()


def test_streaming_with_httpx_client(results):
    """Test streaming with httpx async client."""
    print("\n=== Testing Streaming with HTTPX Client ===")
    
    server_process = None
    try:
        # Create test streaming server
        test_file = Path("temp_httpx_streaming_server.py")
        test_file.write_text("""
import sys
import asyncio
import time
from pathlib import Path

# Add src to path for development  
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from yaapp import Yaapp

app = Yaapp()

@app.expose
async def async_data_stream(delay: float = 0.05, count: int = 3):
    '''Async streaming function for httpx testing.'''
    for i in range(count):
        yield {
            "id": i,
            "data": f"stream_item_{i}",
            "timestamp": time.time(),
            "delay": delay
        }
        await asyncio.sleep(delay)

if __name__ == "__main__":
    app.run()
""")
        
        # Start server
        server_process = subprocess.Popen([
            sys.executable, "temp_httpx_streaming_server.py", "server", "--port", "8897"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(0.1)
        
        try:
            import httpx
        except ImportError:
            results.assert_true(False, "httpx required for async streaming tests. Install with: pip install httpx")
            return
        
        try:
            
            async def test_httpx_streaming():
                """Test streaming with httpx async client."""
                base_url = "http://localhost:8897"
                events = []
                
                async with httpx.AsyncClient() as client:
                    async with client.stream("POST", f"{base_url}/async_data_stream/stream", json={"count": 2, "delay": 0.01}) as response:
                        if response.status_code != 200:
                            return False, f"HTTP {response.status_code}"
                        
                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])
                                    events.append(data)
                                    if len(events) >= 2:  # Get 2 events
                                        break
                                except json.JSONDecodeError:
                                    pass
                
                return len(events) >= 2, events
            
            # Run async test
            success, data = asyncio.run(test_httpx_streaming())
            results.assert_true(success, "HTTPX async client can consume SSE streams")
            
            if success and isinstance(data, list) and len(data) > 0:
                results.assert_true("data" in data[0], "HTTPX client receives proper SSE data")
                results.assert_equal(data[0]["id"], 0, "HTTPX client receives correct event sequence")
                results.assert_true(data[0]["data"].startswith("stream_item_"), "HTTPX client receives expected data format")
            
        except ImportError:
            results.assert_true(False, "httpx required for async streaming tests. Install with: pip install httpx")
        except Exception as e:
            results.assert_true(False, f"HTTPX streaming test failed: {e}")
            
    finally:
        # Cleanup
        if server_process:
            server_process.terminate()
            server_process.wait(timeout=5)
        
        if test_file.exists():
            test_file.unlink()


def test_streaming_examples_integration(results):
    """Test the actual streaming examples."""
    print("\n=== Testing Streaming Examples Integration ===")
    
    server_process = None
    try:
        # Test the actual streaming demo - try multiple possible locations
        demo_paths = [
            Path("../../examples/streaming-demo/app.py").resolve(),
            Path("../examples/streaming-demo/app.py").resolve(),
            Path("examples/streaming-demo/app.py").resolve()
        ]
        
        demo_path = None
        for path in demo_paths:
            if path.exists():
                demo_path = path
                break
        
        if demo_path is None:
            results.assert_true(False, "Streaming demo app.py not found in any expected location")
            return
        
        # Start streaming demo server
        server_process = subprocess.Popen([
            sys.executable, str(demo_path), "server", "--port", "8898"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(0.1)
        
        try:
            import httpx
        except ImportError:
            results.assert_true(False, "httpx required for example integration tests. Install with: pip install httpx")
            return
        
        try:
            
            base_url = "http://localhost:8898"
            
            # Test 1: Regular function endpoint
            with httpx.Client() as client:
                response = client.post(f"{base_url}/regular_function", 
                                     json={"message": "integration_test"})
                if response.status_code == 200:
                    data = response.json()
                    results.assert_equal(data.get("message"), "integration_test", 
                                       "Streaming demo regular endpoint works")
                else:
                    results.assert_true(False, f"Demo regular endpoint failed: {response.status_code}")
            
            # Test 2: Auto counter streaming endpoint
            with httpx.Client() as client:
                with client.stream("POST", f"{base_url}/auto_counter/stream", json={"end": 1}) as response:
                    if response.status_code == 200:
                        events = []
                        for line in response.iter_lines():
                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])
                                    events.append(data)
                                    if len(events) >= 2:  # Get first 2 events
                                        break
                                except json.JSONDecodeError:
                                    pass
                        
                        results.assert_true(len(events) >= 2, "Demo auto_counter stream produces events")
                        if events:
                            results.assert_true("count" in events[0], "Demo events have count field")
                            results.assert_true("timestamp" in events[0], "Demo events have timestamp field")
                    else:
                        results.assert_true(False, f"Demo streaming endpoint failed: {response.status_code}")
            
            # Test 3: Progress simulation streaming endpoint
            with httpx.Client() as client:
                with client.stream("POST", f"{base_url}/simulate_progress/stream", json={"steps": 2}) as response:
                    if response.status_code == 200:
                        events = []
                        for line in response.iter_lines():
                            if line.startswith("data: "):
                                try:
                                    data = json.loads(line[6:])
                                    events.append(data)
                                    if len(events) >= 2:
                                        break
                                except json.JSONDecodeError:
                                    pass
                        
                        results.assert_true(len(events) >= 2, "Demo progress stream produces events")
                        if events:
                            results.assert_true("percentage" in events[0], "Progress events have percentage field")
                            results.assert_true("status" in events[0], "Progress events have status field")
                    else:
                        results.assert_true(False, f"Demo progress endpoint failed: {response.status_code}")
            
        except ImportError:
            results.assert_true(False, "httpx required for example integration tests. Install with: pip install httpx")
        except Exception as e:
            results.assert_true(False, f"Streaming examples integration test failed: {e}")
            
    finally:
        # Cleanup
        if server_process:
            server_process.terminate()
            server_process.wait(timeout=5)


def main():
    """Run all streaming tests."""
    try:
        import httpx
    except ImportError:
        print("⚠️  Streaming dependencies not available: httpx not installed")
        print("✅ Streaming tests skipped gracefully")
        return
    
    print("🌊 YaApp Streaming Tests")
    print("Testing SSE functionality, streaming detection, and client integration.")
    
    results = StreamingTestResults()
    
    # Run all test suites
    test_streaming_detection(results)
    test_sse_server_endpoints(results)
    test_yaapp_client_streaming(results)
    test_streaming_with_httpx_client(results)
    test_streaming_examples_integration(results)
    
    # Show summary
    success = results.summary()
    
    if success:
        print("\n🎉 ALL STREAMING TESTS PASSED!")
        print("Streaming functionality is working correctly.")
    else:
        print("\n💥 STREAMING TESTS FAILED!")
        print("Issues detected in streaming functionality.")
        sys.exit(1)


if __name__ == "__main__":
    main()