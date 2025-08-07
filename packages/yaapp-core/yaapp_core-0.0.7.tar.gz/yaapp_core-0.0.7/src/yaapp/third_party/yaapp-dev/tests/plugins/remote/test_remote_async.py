#!/usr/bin/env python3
"""
Test Remote plugin async functionality.
"""

import pytest
import asyncio
import sys
import os
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, AsyncMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp.plugins.remote.plugin import RemoteProcess, PtyReader, OutputLine


class TestPtyReader:
    """Test PtyReader functionality."""
    
    @pytest.fixture
    def pty_reader(self):
        """Create a PtyReader instance for testing."""
        return PtyReader()
    
    def test_pty_reader_initialization(self, pty_reader):
        """Test PtyReader initialization."""
        assert pty_reader.output_lines == []
        assert pty_reader.current_command == "initial"
        assert pty_reader.reader_task is None
        assert pty_reader.master_fd is None
        assert pty_reader.command_start_index == 0
    
    def test_set_current_command(self, pty_reader):
        """Test setting current command."""
        # Add some initial output
        pty_reader.output_lines = [
            OutputLine("initial", time.time(), "line1", "stdout"),
            OutputLine("initial", time.time(), "line2", "stdout")
        ]
        
        pty_reader.set_current_command("new_command")
        
        assert pty_reader.current_command == "new_command"
        assert pty_reader.command_start_index == 2
    
    def test_get_recent_lines(self, pty_reader):
        """Test getting recent lines."""
        # Add some output lines
        for i in range(10):
            pty_reader.output_lines.append(
                OutputLine("cmd", time.time(), f"line{i}", "stdout")
            )
        
        # Get recent 5 lines
        recent = pty_reader.get_recent_lines(5)
        assert len(recent) == 5
        assert recent[-1].text == "line9"
        
        # Get all lines
        all_lines = pty_reader.get_recent_lines(0)
        assert len(all_lines) == 10
    
    def test_get_current_command_output(self, pty_reader):
        """Test getting current command output."""
        # Add initial output
        pty_reader.output_lines = [
            OutputLine("initial", time.time(), "line1", "stdout"),
            OutputLine("initial", time.time(), "line2", "stdout")
        ]
        
        # Set new command
        pty_reader.set_current_command("new_cmd")
        
        # Add new command output
        pty_reader.output_lines.extend([
            OutputLine("new_cmd", time.time(), "new_line1", "stdout"),
            OutputLine("new_cmd", time.time(), "new_line2", "stdout")
        ])
        
        # Get current command output
        current_output = pty_reader.get_current_command_output()
        assert len(current_output) == 2
        assert current_output[0].text == "new_line1"
        assert current_output[1].text == "new_line2"
    
    @pytest.mark.asyncio
    async def test_pty_reader_start_stop(self, pty_reader):
        """Test PtyReader start and stop."""
        # Mock file descriptor
        mock_fd = 123
        
        with patch.object(pty_reader, '_read_pty') as mock_read:
            mock_read.return_value = None
            
            # Start reader
            await pty_reader.start(mock_fd)
            assert pty_reader.master_fd == mock_fd
            assert pty_reader.reader_task is not None
            
            # Stop reader
            await pty_reader.stop()


class TestRemoteProcess:
    """Test RemoteProcess functionality."""
    
    @pytest.fixture
    def remote_process(self):
        """Create a RemoteProcess instance for testing."""
        return RemoteProcess({})
    
    def test_remote_process_initialization(self, remote_process):
        """Test RemoteProcess initialization."""
        assert remote_process.config == {}
        assert remote_process.yaapp is None
        assert remote_process.process is None
        assert isinstance(remote_process.pty_reader, PtyReader)
        assert remote_process.master_fd is None
        assert remote_process._command_counter == 0
    
    def test_remote_process_with_config(self):
        """Test RemoteProcess initialization with config."""
        config = {"timeout": 60, "shell": "/bin/bash"}
        remote = RemoteProcess(config)
        assert remote.config == config
    
    def test_is_running_no_process(self, remote_process):
        """Test is_running when no process exists."""
        assert remote_process.is_running() is False
    
    def test_is_running_with_process(self, remote_process):
        """Test is_running with mock process."""
        # Mock running process
        mock_process = Mock()
        mock_process.returncode = None
        remote_process.process = mock_process
        
        assert remote_process.is_running() is True
        
        # Mock finished process
        mock_process.returncode = 0
        assert remote_process.is_running() is False
    
    def test_get_status_no_process(self, remote_process):
        """Test get_status when no process exists."""
        status = remote_process.get_status()
        
        assert status["running"] is False
        assert status["pid"] is None
        assert status["returncode"] is None
        assert status["output_lines"] == 0
    
    def test_get_status_with_process(self, remote_process):
        """Test get_status with mock process."""
        # Mock process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.returncode = None
        remote_process.process = mock_process
        
        # Add some output lines
        remote_process.pty_reader.output_lines = [
            OutputLine("cmd", time.time(), "line1", "stdout"),
            OutputLine("cmd", time.time(), "line2", "stdout")
        ]
        
        status = remote_process.get_status()
        
        assert status["running"] is True
        assert status["pid"] == 12345
        assert status["returncode"] is None
        assert status["output_lines"] == 2
    
    def test_start_process_already_running(self, remote_process):
        """Test starting process when one is already running."""
        # Mock running process
        mock_process = Mock()
        mock_process.returncode = None
        remote_process.process = mock_process
        
        result = remote_process.start_process("echo test")
        
        assert "ERROR: A subprocess is already running" in result
    
    @pytest.mark.asyncio
    async def test_start_process_async_success(self, remote_process):
        """Test successful async process start."""
        with patch('pty.openpty') as mock_openpty:
            with patch('termios.tcgetattr') as mock_tcgetattr:
                with patch('termios.tcsetattr') as mock_tcsetattr:
                    with patch('os.get_terminal_size') as mock_get_size:
                        with patch('asyncio.create_subprocess_exec') as mock_create:
                            with patch('os.close') as mock_close:
                                with patch('asyncio.sleep') as mock_sleep:
                                    # Mock PTY creation
                                    mock_openpty.return_value = (10, 11)  # master, slave
                                    mock_tcgetattr.return_value = [0, 0, 0, 0]
                                    mock_get_size.return_value = Mock(lines=24, columns=80)
                                    
                                    # Mock process creation
                                    mock_process = Mock()
                                    mock_process.pid = 12345
                                    mock_process.returncode = None
                                    mock_create.return_value = mock_process
                                    
                                    # Mock PtyReader start
                                    with patch.object(remote_process.pty_reader, 'start') as mock_pty_start:
                                        result = await remote_process._start_process_async("echo test", tail=False)
                                    
                                    assert "Successfully started subprocess" in result
                                    assert remote_process.process == mock_process
                                    assert remote_process.master_fd == 10
                                    mock_pty_start.assert_called_once_with(10)
    
    @pytest.mark.asyncio
    async def test_start_process_async_failure(self, remote_process):
        """Test async process start failure."""
        with patch('pty.openpty') as mock_openpty:
            mock_openpty.side_effect = OSError("PTY creation failed")
            
            result = await remote_process._start_process_async("echo test")
            
            assert "Failed to start subprocess" in result
    
    def test_inject_command_no_process(self, remote_process):
        """Test injecting command when no process is running."""
        result = remote_process.inject_command("ls")
        
        assert "ERROR: No subprocess is currently running" in result
    
    @pytest.mark.asyncio
    async def test_inject_command_async_success(self, remote_process):
        """Test successful async command injection."""
        # Mock running process
        mock_process = Mock()
        mock_process.returncode = None
        remote_process.process = mock_process
        remote_process.master_fd = 10
        
        with patch('os.write') as mock_write:
            with patch('asyncio.sleep') as mock_sleep:
                result = await remote_process._inject_command_async("ls", tail_count=5)
        
        assert "Command injected successfully" in result
        mock_write.assert_called_once_with(10, b"ls\n")
        assert remote_process._command_counter == 1
    
    def test_tail_output_no_process(self, remote_process):
        """Test tailing output when no process is running."""
        result = remote_process.tail_output()
        
        assert "ERROR: No subprocess is currently running" in result
    
    def test_tail_output_with_output(self, remote_process):
        """Test tailing output with available output."""
        # Mock running process
        mock_process = Mock()
        mock_process.returncode = None
        remote_process.process = mock_process
        
        # Add output lines
        remote_process.pty_reader.output_lines = [
            OutputLine("cmd", time.time(), "line1\n", "stdout"),
            OutputLine("cmd", time.time(), "line2\n", "stdout"),
            OutputLine("cmd", time.time(), "line3\n", "stdout")
        ]
        
        result = remote_process.tail_output(count=2)
        
        assert "Recent both output (2 lines)" in result
        assert "line2" in result
        assert "line3" in result
    
    def test_tail_output_no_output(self, remote_process):
        """Test tailing output when no output is available."""
        # Mock running process
        mock_process = Mock()
        mock_process.returncode = None
        remote_process.process = mock_process
        
        result = remote_process.tail_output()
        
        assert "No both output available yet" in result
    
    def test_send_signal_no_process(self, remote_process):
        """Test sending signal when no process is running."""
        result = remote_process.send_signal("SIGINT")
        
        assert "No subprocess is currently running" in result
    
    @pytest.mark.asyncio
    async def test_send_signal_async_sigint(self, remote_process):
        """Test sending SIGINT signal."""
        # Mock running process
        mock_process = Mock()
        mock_process.returncode = None
        remote_process.process = mock_process
        remote_process.master_fd = 10
        
        with patch('os.write') as mock_write:
            result = await remote_process._send_signal_async("SIGINT")
        
        assert "Signal SIGINT sent successfully" in result
        mock_write.assert_called_once_with(10, b"\x03")  # Ctrl+C
    
    @pytest.mark.asyncio
    async def test_send_signal_async_sigterm(self, remote_process):
        """Test sending SIGTERM signal."""
        # Mock running process
        mock_process = Mock()
        mock_process.returncode = None
        remote_process.process = mock_process
        remote_process.master_fd = 10
        
        with patch('os.write') as mock_write:
            result = await remote_process._send_signal_async("SIGTERM")
        
        assert "Signal SIGTERM sent successfully" in result
        mock_write.assert_called_once_with(10, b"\x1c")  # Ctrl+\
    
    @pytest.mark.asyncio
    async def test_send_signal_async_unknown(self, remote_process):
        """Test sending unknown signal."""
        # Mock running process
        mock_process = Mock()
        mock_process.returncode = None
        remote_process.process = mock_process
        remote_process.master_fd = 10
        
        result = await remote_process._send_signal_async("UNKNOWN")
        
        assert "Unknown signal: UNKNOWN" in result
    
    def test_stop_process_no_process(self, remote_process):
        """Test stopping process when none is running."""
        result = remote_process.stop_process()
        
        assert "No subprocess is currently running" in result
    
    @pytest.mark.asyncio
    async def test_stop_process_async_graceful(self, remote_process):
        """Test graceful process stopping."""
        # Mock running process
        mock_process = AsyncMock()
        mock_process.returncode = None
        mock_process.terminate = Mock()
        mock_process.wait = AsyncMock()
        remote_process.process = mock_process
        
        with patch.object(remote_process.pty_reader, 'stop') as mock_pty_stop:
            result = await remote_process._stop_process_async()
        
        assert "Subprocess stopped successfully" in result
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called()
        mock_pty_stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stop_process_async_force_kill(self, remote_process):
        """Test force killing process when graceful stop fails."""
        # Mock running process
        mock_process = AsyncMock()
        mock_process.returncode = None
        mock_process.terminate = Mock()
        mock_process.kill = Mock()
        
        # Mock wait to timeout first, then succeed
        mock_process.wait = AsyncMock(side_effect=[None, None])  # Just return None
        remote_process.process = mock_process
        
        with patch.object(remote_process.pty_reader, 'stop') as mock_pty_stop:
            with patch('asyncio.wait_for', side_effect=[asyncio.TimeoutError(), None]):
                result = await remote_process._stop_process_async()
        
        assert "Subprocess stopped successfully" in result
        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()
        mock_pty_stop.assert_called_once()
    
    def test_send_input_no_process(self, remote_process):
        """Test sending input when no process is running."""
        result = remote_process.send_input("test input")
        
        assert "ERROR: No subprocess is currently running" in result
    
    def test_send_input_success(self, remote_process):
        """Test successful input sending."""
        # Mock running process
        mock_process = Mock()
        mock_process.returncode = None
        remote_process.process = mock_process
        remote_process.master_fd = 10
        
        with patch('os.write') as mock_write:
            result = remote_process.send_input("test input")
        
        assert "Input sent: test input" in result
        mock_write.assert_called_once_with(10, b"test input\n")
    
    def test_send_input_error(self, remote_process):
        """Test input sending error."""
        # Mock running process
        mock_process = Mock()
        mock_process.returncode = None
        remote_process.process = mock_process
        remote_process.master_fd = 10
        
        with patch('os.write') as mock_write:
            mock_write.side_effect = OSError("Write failed")
            result = remote_process.send_input("test input")
        
        assert "ERROR: Failed to send input" in result
    
    @pytest.mark.asyncio
    async def test_start_process_stream(self, remote_process):
        """Test process streaming functionality."""
        with patch.object(remote_process, '_start_process_async') as mock_start:
            mock_start.return_value = "Successfully started subprocess: echo test"
            
            # Mock running process
            mock_process = Mock()
            mock_process.returncode = None
            remote_process.process = mock_process
            
            # Add some output
            remote_process.pty_reader.output_lines = [
                OutputLine("cmd", time.time(), "line1\n", "stdout"),
                OutputLine("cmd", time.time(), "line2\n", "stdout")
            ]
            
            # Collect stream output
            stream_output = []
            async for chunk in remote_process.start_process_stream("echo test"):
                stream_output.append(chunk)
                # Break after a few chunks to avoid infinite loop
                if len(stream_output) >= 3:
                    # Mock process ending
                    mock_process.returncode = 0
            
            assert len(stream_output) >= 1
            assert "Successfully started subprocess" in stream_output[0]
    
    def test_sync_wrapper_methods(self, remote_process):
        """Test that sync wrapper methods handle async context properly."""
        # Test start_process sync wrapper
        with patch.object(remote_process, '_start_process_async') as mock_async:
            with patch('asyncio.run') as mock_run:
                mock_run.return_value = "Success"
                
                result = remote_process.start_process("echo test")
                assert result == "Success"
        
        # Test inject_command sync wrapper
        with patch.object(remote_process, '_inject_command_async') as mock_async:
            with patch('asyncio.run') as mock_run:
                mock_run.return_value = "Command injected"
                
                result = remote_process.inject_command("ls")
                assert result == "Command injected"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])