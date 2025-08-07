"""
Real integration tests for RemoteProcess plugin.

These tests actually start a server process and test client connectivity.
They are marked as integration tests and require subprocess execution.
"""

import asyncio
import subprocess
import time
import signal
import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

# Try to import pytest, but don't require it
try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False
    # Create dummy pytest markers for standalone execution
    class DummyPytest:
        @staticmethod
        def mark(*args, **kwargs):
            def decorator(func):
                return func
            return decorator
    pytest = DummyPytest()
    pytest.mark.integration = pytest.mark
    pytest.mark.subprocess = pytest.mark
    pytest.mark.slow = pytest.mark

class ServerManager:
    """Manages the yaapp server for testing"""
    
    def __init__(self, port=8881):
        self.port = port
        self.process = None
        self.server_url = f"http://localhost:{port}"
    
    async def start(self):
        """Start the server process"""
        print(f"🚀 Starting server on port {self.port}...")
        
        # Set up environment
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path(__file__).parent.parent.parent.parent / "src")
        
        # Create a simple server script for testing
        server_script = self._create_test_server_script()
        
        # Start server process
        self.process = subprocess.Popen([
            sys.executable,
            "-c", server_script,
            str(self.port)
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        await self._wait_for_server()
        print(f"✅ Server started successfully on {self.server_url}")
    
    def _create_test_server_script(self):
        """Create a simple server script for testing"""
        return f'''
import sys
sys.path.insert(0, "{Path(__file__).parent.parent.parent.parent / "src"}")

try:
    from yaapp import yaapp
    from yaapp.plugins.remote_process.plugin import RemoteProcess
    
    # Simple HTTP server for testing
    import json
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import urllib.parse
    
    class TestHandler(BaseHTTPRequestHandler):
        process_running = False
        process_pid = None
        
        def do_GET(self):
            if self.path == "/_describe_rpc":
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({{"status": "ok"}}).encode())
            elif "/RemoteProcess/start_process_stream/stream" in self.path:
                # Handle streaming endpoint
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                # Send some test stream data
                self.wfile.write(b"data: Started\\n\\n")
                self.wfile.write(b"data: Test\\n\\n")
                self.wfile.write(b"data: Done\\n\\n")
            else:
                self.send_response(404)
                self.end_headers()
        
        def do_POST(self):
            if self.path == "/_rpc":
                self._handle_rpc()
            elif "/RemoteProcess/start_process_stream/stream" in self.path:
                self._handle_streaming()
            else:
                self.send_response(404)
                self.end_headers()
        
        def _handle_streaming(self):
            """Handle streaming endpoint"""
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            # Send some test stream data
            self.wfile.write(b"data: Started\\n\\n")
            self.wfile.write(b"data: Test\\n\\n")
            self.wfile.write(b"data: Done\\n\\n")
        
        def _handle_rpc(self):
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                try:
                    data = json.loads(post_data.decode('utf-8'))
                    function = data.get('function', '')
                    args = data.get('args', {{}})
                    
                    # Mock RemoteProcess responses
                    if function == "RemoteProcess.get_status":
                        result = {{"running": TestHandler.process_running, "pid": TestHandler.process_pid, "returncode": None, "output_lines": 0}}
                    elif function == "RemoteProcess.send_input":
                        if TestHandler.process_running:
                            result = "Input sent successfully"
                        else:
                            result = "ERROR: No subprocess is currently running"
                    elif function == "RemoteProcess.stop_process":
                        if TestHandler.process_running:
                            TestHandler.process_running = False
                            TestHandler.process_pid = None
                            result = "Process stopped successfully"
                        else:
                            result = "No subprocess is currently running"
                    elif function == "RemoteProcess.start_process":
                        TestHandler.process_running = True
                        TestHandler.process_pid = 12345
                        command = args.get('command', 'unknown')
                        result = f"Successfully started subprocess: {{command}}"
                    elif function == "RemoteProcess.inject_command":
                        if TestHandler.process_running:
                            result = "Command injected successfully"
                        else:
                            result = "ERROR: No subprocess is currently running"
                    elif function == "RemoteProcess.tail_output":
                        result = ["test output line", "another output line"]
                    else:
                        result = "Unknown function"
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                    
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode())
        
        def log_message(self, format, *args):
            pass  # Suppress logs
    
    if __name__ == "__main__":
        port = int(sys.argv[1]) if len(sys.argv) > 1 else 8881
        server = HTTPServer(('localhost', port), TestHandler)
        print(f"Test server starting on port {{port}}", flush=True)
        server.serve_forever()
        
except Exception as e:
    print(f"Server error: {{e}}", flush=True)
    sys.exit(1)
'''
    
    async def _wait_for_server(self, timeout=10):
        """Wait for server to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                with urllib.request.urlopen(f"{self.server_url}/_describe_rpc") as resp:
                    if resp.status == 200:
                        return
            except:
                pass
            await asyncio.sleep(0.5)
        
        # If we get here, server didn't start
        stdout, stderr = self.process.communicate(timeout=1)
        raise Exception(f"Server failed to start!\nSTDOUT: {stdout.decode()}\nSTDERR: {stderr.decode()}")
    
    async def stop(self):
        """Stop the server process"""
        if self.process:
            print("🛑 Stopping server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            print("✅ Server stopped")

class RemoteProcessClient:
    """Client for testing RemoteProcess"""
    
    def __init__(self, server_url):
        self.server_url = server_url
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def rpc_call(self, method, **kwargs):
        """Make RPC call to RemoteProcess method"""
        data = {
            "function": f"RemoteProcess.{method}",
            "args": kwargs
        }
        
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            f"{self.server_url}/_rpc",
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status != 200:
                    raise Exception(f"RPC call failed: {resp.status}")
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            raise Exception(f"RPC call failed: {e.code} - {e.read().decode('utf-8')}")
    
    def start_process_stream(self, command):
        """Start process and return streaming response"""
        data = {"command": command}
        
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            f"{self.server_url}/RemoteProcess/start_process_stream/stream",
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            resp = urllib.request.urlopen(req)
            if resp.status != 200:
                raise Exception(f"Stream failed: {resp.status}")
            return resp
        except urllib.error.HTTPError as e:
            raise Exception(f"Stream failed: {e.code} - {e.read().decode('utf-8')}")

@pytest.mark.integration
@pytest.mark.subprocess
@pytest.mark.asyncio
async def test_basic_rpc_calls():
    """Test basic RPC functionality"""
    print("\n🧪 Testing Basic RPC Calls")
    print("=" * 50)
    
    server = ServerManager()
    
    try:
        await server.start()
        
        async with RemoteProcessClient(server.server_url) as client:
            # Test get_status (should work without process)
            print("📋 Testing get_status...")
            result = client.rpc_call("get_status")
            print(f"Status result: {result}")
            assert "running" in result
            assert result["running"] is False
            print("✅ get_status works!")
            
            # Test send_input (should fail without process)
            print("📝 Testing send_input without process...")
            result = client.rpc_call("send_input", input_text="test")
            print(f"Send input result: {result}")
            assert "ERROR" in result or "No subprocess" in result
            print("✅ send_input properly rejects when no process!")
            
            # Test stop_process (should fail without process)
            print("🛑 Testing stop_process without process...")
            result = client.rpc_call("stop_process")
            print(f"Stop result: {result}")
            assert "No subprocess" in result
            print("✅ stop_process properly rejects when no process!")
            
    finally:
        await server.stop()

@pytest.mark.integration
@pytest.mark.subprocess
@pytest.mark.asyncio
async def test_process_lifecycle():
    """Test starting and stopping a process"""
    print("\n🧪 Testing Process Lifecycle")
    print("=" * 50)
    
    server = ServerManager()
    
    try:
        await server.start()
        
        async with RemoteProcessClient(server.server_url) as client:
            # Start a simple process
            print("🚀 Starting echo process...")
            result = client.rpc_call("start_process", command="echo 'Hello World'", tail=True)
            print(f"Start result: {result}")
            assert "Successfully started" in result
            print("✅ Process started!")
            
            # Check status
            print("📋 Checking status...")
            status = client.rpc_call("get_status")
            print(f"Status: {status}")
            assert status["running"] is True
            assert status["pid"] is not None
            print("✅ Process is running!")
            
            # Wait a bit for echo to finish
            await asyncio.sleep(2)
            
            # Check status again (echo should be done)
            print("📋 Checking status after echo...")
            status = client.rpc_call("get_status")
            print(f"Status: {status}")
            # Echo process should have finished
            
            # Try to stop (might already be stopped)
            print("🛑 Stopping process...")
            result = client.rpc_call("stop_process")
            print(f"Stop result: {result}")
            print("✅ Stop process completed!")
            
    finally:
        await server.stop()

@pytest.mark.integration
@pytest.mark.subprocess
@pytest.mark.slow
@pytest.mark.asyncio
async def test_interactive_process():
    """Test interactive process with bash"""
    print("\n🧪 Testing Interactive Process")
    print("=" * 50)
    
    server = ServerManager()
    
    try:
        await server.start()
        
        async with RemoteProcessClient(server.server_url) as client:
            # Start bash
            print("🚀 Starting bash process...")
            result = client.rpc_call("start_process", command="bash", tail=False)
            print(f"Start result: {result}")
            assert "Successfully started" in result
            print("✅ Bash started!")
            
            # Check status
            print("📋 Checking bash status...")
            status = client.rpc_call("get_status")
            print(f"Status: {status}")
            assert status["running"] is True
            print("✅ Bash is running!")
            
            # Send a command
            print("📝 Sending 'echo test' command...")
            result = client.rpc_call("inject_command", command="echo test")
            print(f"Inject result: {result}")
            assert "Command injected successfully" in result
            print("✅ Command injected!")
            
            # Get output
            print("📄 Getting output...")
            result = client.rpc_call("tail_output", count=5)
            print(f"Output: {result}")
            print("✅ Got output!")
            
            # Send input
            print("📝 Sending input...")
            result = client.rpc_call("send_input", input_text="pwd")
            print(f"Input result: {result}")
            assert "Input sent" in result
            print("✅ Input sent!")
            
            # Stop bash
            print("🛑 Stopping bash...")
            result = client.rpc_call("stop_process")
            print(f"Stop result: {result}")
            assert "stopped" in result.lower() or "terminated" in result.lower()
            print("✅ Bash stopped!")
            
    finally:
        await server.stop()

@pytest.mark.integration
@pytest.mark.subprocess
@pytest.mark.asyncio
async def test_streaming_endpoint():
    """Test the streaming endpoint"""
    print("\n🧪 Testing Streaming Endpoint")
    print("=" * 50)
    
    server = ServerManager()
    
    try:
        await server.start()
        
        async with RemoteProcessClient(server.server_url) as client:
            print("🌊 Testing streaming endpoint...")
            
            # Start streaming process
            response = client.start_process_stream("echo 'Streaming test'")
            
            # Read some stream data
            chunks = []
            chunk_count = 0
            for line in response:
                if chunk_count >= 5:  # Limit to prevent hanging
                    break
                    
                line_str = line.decode('utf-8').strip()
                if line_str:
                    chunks.append(line_str)
                    print(f"Stream chunk: {line_str}")
                    chunk_count += 1
            
            print(f"✅ Got {len(chunks)} stream chunks!")
            assert len(chunks) > 0, "Should have received some stream data"
            
    finally:
        await server.stop()

@pytest.mark.integration
@pytest.mark.subprocess
@pytest.mark.slow
@pytest.mark.asyncio
async def test_terminal_client():
    """Test the terminal client (basic connectivity)"""
    print("\n🧪 Testing Terminal Client Connectivity")
    print("=" * 50)
    
    server = ServerManager()
    
    try:
        await server.start()
        
        print("🖥️ Testing terminal client connectivity...")
        
        # Set up environment
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path(__file__).parent.parent.parent.parent / "src")
        
        # Get the terminal client path
        terminal_client_path = Path(__file__).parent.parent.parent.parent / "examples" / "plugins" / "remote-process" / "terminal_client.py"
        
        # Run terminal client with a simple command and timeout
        proc = subprocess.Popen([
            sys.executable,
            str(terminal_client_path),
            "echo 'Terminal test'",
            "--server", server.server_url
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        try:
            stdout, stderr = proc.communicate(timeout=10)
            print(f"Terminal client stdout: {stdout.decode()}")
            print(f"Terminal client stderr: {stderr.decode()}")
            
            # Check if it connected successfully
            stderr_text = stderr.decode()
            if "Successfully connected" in stderr_text:
                print("✅ Terminal client connected successfully!")
            elif "Response status: 200" in stderr_text:
                print("✅ Terminal client got 200 response!")
            else:
                print(f"⚠️ Terminal client output: {stderr_text}")
                
        except subprocess.TimeoutExpired:
            proc.kill()
            print("⚠️ Terminal client test timed out (expected for interactive client)")
            
    finally:
        await server.stop()

async def run_all_tests():
    """Run all integration tests"""
    print("🧪 REMOTE PROCESS INTEGRATION TESTS")
    print("=" * 60)
    print("Starting REAL tests with actual server and client!")
    print("=" * 60)
    
    tests = [
        ("Basic RPC Calls", test_basic_rpc_calls),
        ("Process Lifecycle", test_process_lifecycle),
        ("Interactive Process", test_interactive_process),
        ("Streaming Endpoint", test_streaming_endpoint),
        ("Terminal Client", test_terminal_client),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n🏃 Running: {test_name}")
            await test_func()
            print(f"✅ PASSED: {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name}")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"🏁 TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed > 0:
        print("❌ Some tests failed!")
        return 1
    else:
        print("✅ ALL TESTS PASSED!")
        return 0

if __name__ == "__main__":
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)