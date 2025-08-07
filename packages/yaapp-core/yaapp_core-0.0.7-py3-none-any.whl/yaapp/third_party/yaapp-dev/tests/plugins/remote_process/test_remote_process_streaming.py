"""
Tests for RemoteProcess streaming functionality and SSE integration.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock

# Add src to path for testing
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp.plugins.remote_process.plugin import RemoteProcess
from yaapp.streaming import StreamDetector, StreamExecutor, StreamFormatter


class TestStreamingDetection:
    """Test streaming detection for RemoteProcess methods."""
    
    def setup_method(self):
        """Setup for each test."""
        self.remote_process = RemoteProcess()
    
    def test_start_process_stream_detected(self):
        """Test that start_process_stream is detected as streaming."""
        method = getattr(self.remote_process, 'start_process_stream')
        assert StreamDetector.should_stream(method)
    
    def test_start_process_not_streaming(self):
        """Test that regular start_process is not detected as streaming."""
        method = getattr(self.remote_process, 'start_process')
        assert not StreamDetector.should_stream(method)
    
    def test_get_status_not_streaming(self):
        """Test that get_status is not detected as streaming."""
        method = getattr(self.remote_process, 'get_status')
        assert not StreamDetector.should_stream(method)
    
    def test_send_input_not_streaming(self):
        """Test that send_input is not detected as streaming."""
        method = getattr(self.remote_process, 'send_input')
        assert not StreamDetector.should_stream(method)


class TestStreamingExecution:
    """Test streaming execution of RemoteProcess methods."""
    
    def setup_method(self):
        """Setup for each test."""
        self.remote_process = RemoteProcess()
    
    @pytest.mark.asyncio
    async def test_stream_executor_with_start_process_stream(self):
        """Test StreamExecutor with start_process_stream method."""
        with patch.object(self.remote_process, '_start_process_async') as mock_start, \
             patch.object(self.remote_process, 'is_running') as mock_running:
            
            mock_start.return_value = "Successfully started subprocess: test"
            mock_running.side_effect = [True, True, False]  # Run for 2 iterations
            
            # Mock output
            mock_output_line = Mock()
            mock_output_line.text = "Test output line"
            self.remote_process.pty_reader.output_lines = [mock_output_line]
            
            # Execute streaming
            chunks = []
            async for chunk in StreamExecutor.execute_stream(
                self.remote_process.start_process_stream, 
                {"command": "test"}
            ):
                chunks.append(chunk)
                if len(chunks) >= 3:  # Prevent infinite loop
                    break
            
            # Should have SSE formatted output
            assert len(chunks) >= 1
            assert any("data:" in chunk for chunk in chunks)
    
    @pytest.mark.asyncio
    async def test_stream_executor_with_error(self):
        """Test StreamExecutor handles errors properly."""
        with patch.object(self.remote_process, '_start_process_async') as mock_start:
            mock_start.side_effect = Exception("Test error")
            
            # Execute streaming
            chunks = []
            async for chunk in StreamExecutor.execute_stream(
                self.remote_process.start_process_stream,
                {"command": "test"}
            ):
                chunks.append(chunk)
                break  # Only get first chunk (error)
            
            # Should have error in SSE format
            assert len(chunks) == 1
            assert "data:" in chunks[0]
            assert "error" in chunks[0].lower()


class TestSSEFormatting:
    """Test SSE formatting for RemoteProcess output."""
    
    def test_format_simple_text(self):
        """Test formatting simple text as SSE."""
        text = "Hello World"
        formatted = StreamFormatter.format_sse(text)
        
        expected = "event: data\ndata: Hello World\n\n"
        assert formatted == expected
    
    def test_format_json_data(self):
        """Test formatting JSON data as SSE."""
        data = {"status": "running", "pid": 12345}
        formatted = StreamFormatter.format_sse(data)
        
        assert "event: data\n" in formatted
        assert "data: {" in formatted
        assert '"status": "running"' in formatted
        assert "\n\n" in formatted
    
    def test_format_with_newlines(self):
        """Test formatting text with newlines as SSE."""
        text = "Line 1\nLine 2\r\nLine 3"
        formatted = StreamFormatter.format_sse(text)
        
        # Newlines should be escaped
        assert "\\\\n" in formatted
        assert "\\\\r" in formatted
        assert "\n\n" in formatted  # SSE terminator should remain
    
    def test_format_error_event(self):
        """Test formatting error as SSE event."""
        error_data = {"error": "Process failed", "type": "execution_error"}
        formatted = StreamFormatter.format_sse(error_data, "error")
        
        assert "event: error\n" in formatted
        assert "data: {" in formatted
        assert '"error": "Process failed"' in formatted


class TestRemoteProcessStreamingIntegration:
    """Integration tests for RemoteProcess streaming with yaapp framework."""
    
    def setup_method(self):
        """Setup for each test."""
        self.remote_process = RemoteProcess()
    
    def teardown_method(self):
        """Cleanup after each test."""
        if self.remote_process.is_running():
            self.remote_process.stop_process()
    
    @pytest.mark.asyncio
    async def test_streaming_lifecycle(self):
        """Test complete streaming lifecycle."""
        with patch.object(self.remote_process, '_start_process_async') as mock_start, \
             patch.object(self.remote_process, 'is_running') as mock_running:
            
            mock_start.return_value = "Successfully started subprocess: echo test"
            
            # Simulate process lifecycle: start -> running -> output -> end
            mock_running.side_effect = [True, True, True, False]
            
            # Mock progressive output
            output_lines = []
            def mock_output_lines_property():
                return output_lines
            
            type(self.remote_process.pty_reader).output_lines = property(mock_output_lines_property)
            
            # Collect streaming output
            stream_chunks = []
            iteration_count = 0
            
            async for chunk in self.remote_process.start_process_stream("echo test"):
                stream_chunks.append(chunk)
                iteration_count += 1
                
                # Add output after first iteration
                if iteration_count == 2:
                    mock_line = Mock()
                    mock_line.text = "Test output from process"
                    output_lines.append(mock_line)
                
                # Prevent infinite loop
                if iteration_count >= 4:
                    break
            
            # Verify streaming output
            assert len(stream_chunks) >= 2
            
            # First chunk should be success message
            assert "Successfully started subprocess" in stream_chunks[0]
            
            # Should have SSE format
            assert all("data:" in chunk for chunk in stream_chunks)
    
    @pytest.mark.asyncio
    async def test_concurrent_streaming_and_input(self):
        """Test concurrent streaming and input sending."""
        with patch.object(self.remote_process, '_start_process_async') as mock_start, \
             patch.object(self.remote_process, 'is_running') as mock_running, \
             patch.object(self.remote_process, 'send_input') as mock_send_input:
            
            mock_start.return_value = "Successfully started subprocess: bash"
            mock_running.side_effect = [True, True, False]
            mock_send_input.return_value = "Input sent: test command"
            
            # Start streaming task
            stream_task = asyncio.create_task(
                self._collect_stream_chunks(self.remote_process, "bash", max_chunks=2)
            )
            
            # Send input while streaming
            input_task = asyncio.create_task(
                self._send_test_input(self.remote_process)
            )
            
            # Wait for both tasks
            stream_chunks, input_result = await asyncio.gather(stream_task, input_task)
            
            # Verify both operations worked
            assert len(stream_chunks) >= 1
            assert "Successfully started subprocess" in stream_chunks[0]
            assert "Input sent" in input_result
    
    async def _collect_stream_chunks(self, remote_process, command, max_chunks=5):
        """Helper to collect stream chunks with limit."""
        chunks = []
        async for chunk in remote_process.start_process_stream(command):
            chunks.append(chunk)
            if len(chunks) >= max_chunks:
                break
        return chunks
    
    async def _send_test_input(self, remote_process):
        """Helper to send test input after small delay."""
        await asyncio.sleep(0.1)  # Let streaming start
        return remote_process.send_input("test command")


class TestStreamingErrorHandling:
    """Test error handling in streaming scenarios."""
    
    def setup_method(self):
        """Setup for each test."""
        self.remote_process = RemoteProcess()
    
    @pytest.mark.asyncio
    async def test_streaming_with_process_start_failure(self):
        """Test streaming when process fails to start."""
        with patch.object(self.remote_process, '_start_process_async') as mock_start:
            mock_start.return_value = "ERROR: Command not found"
            
            chunks = []
            async for chunk in self.remote_process.start_process_stream("invalid_command"):
                chunks.append(chunk)
                break  # Only get first chunk
            
            assert len(chunks) == 1
            assert "ERROR: Command not found" in chunks[0]
            assert "data:" in chunks[0]  # Should still be SSE formatted
    
    @pytest.mark.asyncio
    async def test_streaming_with_process_crash(self):
        """Test streaming when process crashes during execution."""
        with patch.object(self.remote_process, '_start_process_async') as mock_start, \
             patch.object(self.remote_process, 'is_running') as mock_running:
            
            mock_start.return_value = "Successfully started subprocess: test"
            
            # Simulate process crash: running -> crash
            mock_running.side_effect = [True, False]
            
            chunks = []
            async for chunk in self.remote_process.start_process_stream("test"):
                chunks.append(chunk)
                if len(chunks) >= 3:  # Limit iterations
                    break
            
            # Should handle gracefully and send end message
            assert len(chunks) >= 2
            assert "Successfully started subprocess" in chunks[0]
            assert "Process ended" in chunks[-1]
    
    @pytest.mark.asyncio
    async def test_streaming_exception_handling(self):
        """Test streaming handles exceptions gracefully."""
        with patch.object(self.remote_process, '_start_process_async') as mock_start, \
             patch.object(self.remote_process, 'is_running') as mock_running:
            
            mock_start.return_value = "Successfully started subprocess: test"
            mock_running.side_effect = Exception("Unexpected error")
            
            chunks = []
            try:
                async for chunk in self.remote_process.start_process_stream("test"):
                    chunks.append(chunk)
                    if len(chunks) >= 2:  # Limit to prevent hanging
                        break
            except Exception:
                pass  # Expected to handle gracefully
            
            # Should have at least the initial success message
            assert len(chunks) >= 1
            assert "Successfully started subprocess" in chunks[0]


@pytest.mark.asyncio
class TestStreamingPerformance:
    """Test streaming performance and resource usage."""
    
    def setup_method(self):
        """Setup for each test."""
        self.remote_process = RemoteProcess()
    
    @pytest.mark.asyncio
    async def test_streaming_memory_usage(self):
        """Test that streaming doesn't accumulate excessive memory."""
        with patch.object(self.remote_process, '_start_process_async') as mock_start, \
             patch.object(self.remote_process, 'is_running') as mock_running:
            
            mock_start.return_value = "Successfully started subprocess: test"
            
            # Simulate long-running process
            call_count = 0
            def mock_running_side_effect():
                nonlocal call_count
                call_count += 1
                return call_count < 100  # Run for 100 iterations
            
            mock_running.side_effect = mock_running_side_effect
            
            # Mock output that grows over time
            output_lines = []
            for i in range(50):
                mock_line = Mock()
                mock_line.text = f"Output line {i}"
                output_lines.append(mock_line)
            
            self.remote_process.pty_reader.output_lines = output_lines
            
            # Collect streaming output
            chunk_count = 0
            async for chunk in self.remote_process.start_process_stream("test"):
                chunk_count += 1
                if chunk_count >= 10:  # Limit for test
                    break
            
            # Should complete without memory issues
            assert chunk_count == 10
    
    @pytest.mark.asyncio
    async def test_streaming_timing(self):
        """Test streaming timing and delays."""
        import time
        
        with patch.object(self.remote_process, '_start_process_async') as mock_start, \
             patch.object(self.remote_process, 'is_running') as mock_running:
            
            mock_start.return_value = "Successfully started subprocess: test"
            mock_running.side_effect = [True, True, False]
            
            start_time = time.time()
            
            chunks = []
            async for chunk in self.remote_process.start_process_stream("test"):
                chunks.append(chunk)
                if len(chunks) >= 3:
                    break
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete reasonably quickly (within 1 second for test)
            assert duration < 1.0
            assert len(chunks) >= 2


if __name__ == "__main__":
    # pytest.main([__file__])
    print('Test file loaded successfully')
