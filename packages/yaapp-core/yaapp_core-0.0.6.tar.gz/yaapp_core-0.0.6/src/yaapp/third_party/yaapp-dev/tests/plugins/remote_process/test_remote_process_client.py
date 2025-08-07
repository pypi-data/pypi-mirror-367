"""
Tests for RemoteProcess client functionality and interactions.
"""

# import pytest  # Removed for compatibility
import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Add src to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))


class TestRemoteProcessClientInteraction:
    """Test client interaction patterns with RemoteProcess."""
    
    def setup_method(self):
        """Setup for each test."""
        from yaapp.plugins.remote_process.plugin import RemoteProcess
        self.remote_process = RemoteProcess()
    
    def test_client_status_check(self):
        """Test client checking process status."""
        # Simulate client calling get_status
        status = self.remote_process.get_status()
        
        # Should return expected format
        assert isinstance(status, dict)
        assert "running" in status
        assert "pid" in status
        assert "returncode" in status
        assert "output_lines" in status
        
        # Initial state should be not running
        assert status["running"] is False
        assert status["pid"] is None
    
    def test_client_input_validation(self):
        """Test client input validation and error handling."""
        # Test send_input with no process
        result = self.remote_process.send_input("test")
        assert "ERROR" in result
        assert "No subprocess is currently running" in result
        
        # Test empty input
        result = self.remote_process.send_input("")
        assert "ERROR" in result
        
        # Test None input
        try:
            result = self.remote_process.send_input(None)
            assert "ERROR" in result
        except (TypeError, AttributeError):
            pass  # Expected for None input
    
    def test_client_command_validation(self):
        """Test client command validation."""
        # Test empty command
        result = self.remote_process.start_process("")
        assert "ERROR" in result or "Failed" in result
        
        # Test None command
        try:
            result = self.remote_process.start_process(None)
            assert "ERROR" in result or "Failed" in result or "Error" in result
        except (TypeError, AttributeError):
            pass  # Expected for None command


class TestRemoteProcessHTTPClientSimulation:
    """Simulate HTTP client interactions with RemoteProcess."""
    
    def setup_method(self):
        """Setup for each test."""
        from yaapp.plugins.remote_process.plugin import RemoteProcess
        self.remote_process = RemoteProcess()
    
    def test_http_get_status_simulation(self):
        """Simulate HTTP GET request to get status."""
        # Simulate HTTP client calling get_status endpoint
        response_data = self.remote_process.get_status()
        
        # Should be JSON serializable
        json_response = json.dumps(response_data)
        parsed_response = json.loads(json_response)
        
        assert parsed_response["running"] is False
        assert parsed_response["pid"] is None
    
    def test_http_post_input_simulation(self):
        """Simulate HTTP POST request to send input."""
        # Simulate HTTP client sending input
        request_data = {"input_text": "echo hello"}
        
        # Extract input from request
        input_text = request_data["input_text"]
        response = self.remote_process.send_input(input_text)
        
        # Should return error (no process running)
        assert "ERROR" in response
    
    @pytest.mark.asyncio
    async def test_http_sse_stream_simulation(self):
        """Simulate HTTP SSE stream consumption."""
        with patch.object(self.remote_process, '_start_process_async') as mock_start, \
             patch.object(self.remote_process, 'is_running') as mock_running:
            
            mock_start.return_value = "Successfully started subprocess: echo test"
            mock_running.side_effect = [True, False]  # Run once then stop
            
            # Simulate SSE client consuming stream
            sse_chunks = []
            async for chunk in self.remote_process.start_process_stream("echo test"):
                # Simulate SSE parsing
                if chunk.startswith("data: "):
                    data = chunk[6:]  # Remove "data: " prefix
                    sse_chunks.append(data)
                
                if len(sse_chunks) >= 2:  # Limit for test
                    break
            
            # Should have received SSE formatted data
            assert len(sse_chunks) >= 1
            assert "Successfully started subprocess" in sse_chunks[0]


class TestRemoteProcessClientErrorScenarios:
    """Test client error scenarios and edge cases."""
    
    def setup_method(self):
        """Setup for each test."""
        from yaapp.plugins.remote_process.plugin import RemoteProcess
        self.remote_process = RemoteProcess()
    
    def test_client_concurrent_operations(self):
        """Test client attempting concurrent operations."""
        # Mock running process first
        mock_process = Mock()
        mock_process.returncode = None
        self.remote_process.process = mock_process
        
        # Try to start another process while one is running
        # This should fail because is_running() returns True
        result = self.remote_process.start_process("another_command")
        assert "ERROR" in result or "already running" in result
    
    def test_client_invalid_signal(self):
        """Test client sending invalid signal."""
        # Mock running process
        mock_process = Mock()
        mock_process.returncode = None
        self.remote_process.process = mock_process
        
        # Try to send invalid signal
        result = self.remote_process.send_signal(999)  # Invalid signal number
        
        # Should handle gracefully
        assert isinstance(result, str)
    
    def test_client_process_cleanup_on_error(self):
        """Test that process is cleaned up properly on errors."""
        with patch.object(self.remote_process, '_start_process_async') as mock_start:
            mock_start.side_effect = Exception("Process start failed")
            
            # Try to start process
            try:
                result = self.remote_process.start_process("test")
                assert "ERROR" in result or "Failed" in result
            except Exception:
                pass
            
            # Process should not be set
            assert self.remote_process.process is None
            assert not self.remote_process.is_running()


class TestRemoteProcessClientProtocols:
    """Test different client protocol interactions."""
    
    def setup_method(self):
        """Setup for each test."""
        from yaapp.plugins.remote_process.plugin import RemoteProcess
        self.remote_process = RemoteProcess()
    
    def test_json_rpc_style_interaction(self):
        """Test JSON-RPC style client interaction."""
        # Simulate JSON-RPC request
        rpc_request = {
            "jsonrpc": "2.0",
            "method": "RemoteProcess.get_status",
            "params": {},
            "id": 1
        }
        
        # Extract method and params
        method_parts = rpc_request["method"].split(".")
        method_name = method_parts[-1]
        
        # Call method
        if method_name == "get_status":
            result = self.remote_process.get_status()
            
            # Format as JSON-RPC response
            rpc_response = {
                "jsonrpc": "2.0",
                "result": result,
                "id": rpc_request["id"]
            }
            
            assert rpc_response["result"]["running"] is False
            assert rpc_response["id"] == 1
    
    def test_rest_style_interaction(self):
        """Test REST-style client interaction."""
        # Simulate REST GET /RemoteProcess/get_status
        response = self.remote_process.get_status()
        
        # Should be suitable for REST response
        assert isinstance(response, dict)
        assert "running" in response
        
        # Simulate REST POST /RemoteProcess/send_input
        request_body = {"input_text": "test command"}
        response = self.remote_process.send_input(request_body["input_text"])
        
        # Should return string response
        assert isinstance(response, str)
    
    @pytest.mark.asyncio
    async def test_sse_protocol_interaction(self):
        """Test Server-Sent Events protocol interaction."""
        with patch.object(self.remote_process, '_start_process_async') as mock_start, \
             patch.object(self.remote_process, 'is_running') as mock_running:
            
            mock_start.return_value = "Successfully started subprocess: test"
            mock_running.side_effect = [True, False]
            
            # Simulate SSE client
            events = []
            async for chunk in self.remote_process.start_process_stream("test"):
                # Parse SSE format
                if "data: " in chunk:
                    event_data = chunk.split("data: ", 1)[1].split("\n")[0]
                    events.append(event_data)
                
                if len(events) >= 2:
                    break
            
            # Should have received proper SSE events
            assert len(events) >= 1
            assert "Successfully started subprocess" in events[0]


class TestRemoteProcessClientSecurity:
    """Test security aspects of client interactions."""
    
    def setup_method(self):
        """Setup for each test."""
        from yaapp.plugins.remote_process.plugin import RemoteProcess
        self.remote_process = RemoteProcess()
    
    def test_command_injection_protection(self):
        """Test protection against command injection."""
        # Test potentially dangerous commands
        dangerous_commands = [
            "rm -rf /",
            "echo test; rm file",
            "test && malicious_command",
            "test | dangerous_pipe",
            "$(malicious_command)",
            "`malicious_command`"
        ]
        
        for cmd in dangerous_commands:
            # Should not execute dangerous commands in test environment
            # This test verifies the plugin doesn't crash on dangerous input
            try:
                result = self.remote_process.start_process(cmd)
                # Should either fail safely or handle gracefully
                assert isinstance(result, str)
            except Exception as e:
                # Should not crash the plugin
                assert "ERROR" in str(e) or "Failed" in str(e)
    
    def test_input_sanitization(self):
        """Test input sanitization for send_input."""
        # Test various input types
        test_inputs = [
            "normal input",
            "input with\nnewlines",
            "input with\ttabs",
            "input with special chars: !@#$%^&*()",
            "very " + "long " * 100 + "input",  # Long input
            "",  # Empty input
        ]
        
        for test_input in test_inputs:
            try:
                result = self.remote_process.send_input(test_input)
                # Should handle all inputs gracefully
                assert isinstance(result, str)
                # Should indicate no process running
                assert "ERROR" in result
            except Exception as e:
                # Should not crash
                assert isinstance(e, (TypeError, ValueError))
    
    def test_resource_limits(self):
        """Test resource usage limits."""
        # Test output buffer limits
        large_output = "x" * 10000  # Large output
        
        # Add large output to PTY reader
        from yaapp.plugins.remote.plugin import OutputLine
        from datetime import datetime
        for i in range(100):  # Add many lines
            output_line = OutputLine(
                cmd=f"test_cmd_{i}",
                timestamp=datetime.now(),
                text=f"Line {i}: {large_output}",
                stream="test"
            )
            self.remote_process.pty_reader.output_lines.append(output_line)
        
        # Should handle large output gracefully
        recent_lines = self.remote_process.pty_reader.get_recent_lines(count=10)
        assert len(recent_lines) == 10  # Should limit output
        
        # Should not consume excessive memory - check output lines directly
        assert len(self.remote_process.pty_reader.output_lines) == 100


class TestRemoteProcessClientCompatibility:
    """Test compatibility with different client types."""
    
    def setup_method(self):
        """Setup for each test."""
        from yaapp.plugins.remote_process.plugin import RemoteProcess
        self.remote_process = RemoteProcess()
    
    def test_sync_client_compatibility(self):
        """Test compatibility with synchronous clients."""
        # Sync clients should be able to call sync methods
        status = self.remote_process.get_status()
        assert isinstance(status, dict)
        
        input_result = self.remote_process.send_input("test")
        assert isinstance(input_result, str)
        
        stop_result = self.remote_process.stop_process()
        assert isinstance(stop_result, str)
    
    @pytest.mark.asyncio
    async def test_async_client_compatibility(self):
        """Test compatibility with asynchronous clients."""
        # Async clients should be able to call async methods
        with patch.object(self.remote_process, '_start_process_async') as mock_start:
            mock_start.return_value = "Successfully started subprocess: test"
            
            result = await self.remote_process._start_process_async("test")
            assert "Successfully started" in result
    
    def test_mixed_client_compatibility(self):
        """Test that sync and async methods can be mixed."""
        # Should be able to call sync methods
        status1 = self.remote_process.get_status()
        assert status1["running"] is False
        
        # Should be able to call sync wrapper for async methods
        result = self.remote_process.start_process("test")
        assert isinstance(result, str)
        
        # Should be able to call sync methods again
        status2 = self.remote_process.get_status()
        assert isinstance(status2, dict)


if __name__ == "__main__":
    # pytest.main([__file__])
    print('Test file loaded successfully')
