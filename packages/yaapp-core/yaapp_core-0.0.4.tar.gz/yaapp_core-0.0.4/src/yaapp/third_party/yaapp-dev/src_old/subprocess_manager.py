"""
Subprocess Manager MCP Plugin

Clean 3-tool interface for subprocess management:
1. start - Start a subprocess
2. run - Inject command and tail output  
3. tail - Just tail output streams

All output includes timestamps for proper interleaving.
"""

import asyncio
import logging
import os
import pty
import re
import select
import termios
from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal, Optional

from fastmcp import Context, FastMCP

logger = logging.getLogger(__name__)

@dataclass
class OutputLine:
    """Represents a line of output from the subprocess"""
    cmd: str
    timestamp: datetime
    text: str
    stream: str  # 'stdout' or 'stderr'

class PtyReader:
    """Reads from a PTY master fd and tracks output with command association"""
    
    def __init__(self):
        self.output_lines: List[OutputLine] = []
        self.current_command: str = "initial"
        self.reader_task: Optional[asyncio.Task] = None
        self.master_fd: Optional[int] = None
        self.command_start_index: int = 0  # Track where current command output starts
        
    def set_current_command(self, cmd: str):
        """Update the current command being executed and mark the start position"""
        self.current_command = cmd
        self.command_start_index = len(self.output_lines)  # Mark where new command output starts
        logger.info(f"PtyReader: Command set to '{cmd}', start index: {self.command_start_index}")
    
    async def start(self, master_fd: int):
        """Start reading from the PTY master fd asynchronously"""
        self.master_fd = master_fd
        self.reader_task = asyncio.create_task(self._read_pty())
        logger.info(f"PtyReader: Started reading from master fd {master_fd}")
        
    async def _read_pty(self):
        """Internal method to read from PTY continuously"""
        try:
            loop = asyncio.get_event_loop()
            
            while True:
                # Use asyncio to read from fd in a non-blocking way
                data = await loop.run_in_executor(None, self._read_fd_chunk)
                if not data:
                    # Small delay to prevent busy waiting
                    await asyncio.sleep(0.01)
                    continue
                    
                # Process text - preserve ANSI sequences for terminal display
                text = data.decode('utf-8', errors='replace')
                # Note: ANSI sequences are preserved for proper terminal rendering
                
                # Don't split into lines - preserve the raw text with newlines
                if text:
                    output_line = OutputLine(
                        cmd=self.current_command,
                        timestamp=datetime.now(),
                        text=text,
                        stream="pty"  # PTY merges stdout/stderr
                    )
                    self.output_lines.append(output_line)
                    logger.info(f"pty: {repr(text)}")
                        
        except Exception as e:
            logger.error(f"Error reading from PTY: {e}")
    
    def _strip_ansi_sequences(self, text: str) -> str:
        """Remove ANSI escape sequences and control characters"""
        # Comprehensive ANSI escape sequence removal
        # CSI sequences: ESC [ ... (A-Z, a-z, @, `, |, }, ~)
        text = re.sub(r'\x1b\[[0-9;?]*[A-Za-z@`|{}~]', '', text)
        
        # OSC sequences: ESC ] ... BEL/ST
        text = re.sub(r'\x1b\].*?(?:\x07|\x1b\\\\)', '', text)
        
        # Other escape sequences
        text = re.sub(r'\x1b[\\(\\)#%]', '', text)  # Character set selection
        text = re.sub(r'\x1b[><= ]', '', text)       # Various modes
        
        # Control characters (except newline, tab, carriage return)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # Bracketed paste mode
        text = re.sub(r'\x1b\[\\?2004[hl]', '', text)
        
        return text
    
    def _read_fd_chunk(self) -> bytes:
        """Read a chunk from the PTY fd (runs in executor)"""
        try:
            if self.master_fd is not None:
                # Use select to check if data is available
                import select
                ready, _, _ = select.select([self.master_fd], [], [], 0.1)
                if ready:
                    return os.read(self.master_fd, 4096)
        except (OSError, select.error):
            pass
        return b''
            
    def get_recent_lines(self, count: int = 10) -> List[OutputLine]:
        """Get recent output lines"""
        return self.output_lines[-count:] if count > 0 else self.output_lines
    
    def get_current_command_output(self) -> List[OutputLine]:
        """Get output lines from the current command only"""
        if self.command_start_index >= len(self.output_lines):
            return []
        return self.output_lines[self.command_start_index:]
    
    async def stop(self):
        """Stop the PTY reader"""
        if self.reader_task:
            self.reader_task.cancel()
            try:
                await self.reader_task
            except asyncio.CancelledError:
                pass
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
        logger.info("PtyReader: Stopped")

class SubprocessManager:
    """Manages a subprocess with PTY for proper interactive behavior"""
    
    def __init__(self):
        self.process: Optional[asyncio.subprocess.Process] = None
        self.pty_reader = PtyReader()
        self.master_fd: Optional[int] = None
        self._command_counter = 0
        
    async def start_process(self, command: List[str]) -> bool:
        """Start the subprocess with PTY for proper interactive behavior"""
        master_fd = None
        slave_fd = None
        
        try:
            # Create pseudo-terminal
            master_fd, slave_fd = pty.openpty()
            
            # Configure slave terminal for interactive use
            slave_attr = termios.tcgetattr(slave_fd)
            # Disable echo to prevent double echoing
            slave_attr[3] = slave_attr[3] & ~termios.ECHO
            termios.tcsetattr(slave_fd, termios.TCSADRAIN, slave_attr)
            
            # Set terminal size for proper ANSI rendering
            try:
                import struct, fcntl
                # Get current terminal size
                terminal_size = os.get_terminal_size()
                winsize = struct.pack('HHHH', terminal_size.lines, terminal_size.columns, 0, 0)
                fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)
            except (OSError, AttributeError):
                # Fallback to common size if can't detect
                winsize = struct.pack('HHHH', 24, 80, 0, 0)
                try:
                    fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, winsize)
                except OSError:
                    pass
            
            # Start process with PTY - run EXACTLY what user specified
            self.process = await asyncio.create_subprocess_exec(
                *command,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                preexec_fn=os.setsid,  # Enable job control
                env=os.environ  # Use EXACTLY the user's environment
            )
            
            # Close slave fd in parent process (we only need master_fd)
            os.close(slave_fd)
            slave_fd = None  # Mark as closed
            
            # Store master_fd and start PTY reader
            self.master_fd = master_fd
            await self.pty_reader.start(self.master_fd)
            
            logger.info(f"Started subprocess with PTY: {' '.join(command)} (PID: {self.process.pid})")
            
            # Wait for subprocess to initialize and show natural prompt
            await asyncio.sleep(1.0)  # Give subprocess time to show its prompt naturally
            
            # Check if process is still running
            if self.process.returncode is not None:
                logger.error(f"Process exited immediately with code {self.process.returncode}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to start subprocess: {e}")
            return False
            
        finally:
            # Cleanup FDs on error
            if slave_fd is not None:
                try:
                    os.close(slave_fd)
                except OSError:
                    pass
            
            # If we failed and have master_fd, clean it up
            if not hasattr(self, 'master_fd') or self.master_fd != master_fd:
                if master_fd is not None:
                    try:
                        os.close(master_fd)
                    except OSError:
                        pass
    
    async def inject_command(self, cmd: str) -> tuple[bool, int]:
        """Inject a command into the subprocess via PTY and return the starting line count"""
        if not self.process or self.master_fd is None:
            return False, 0
            
        try:
            # Get current line count before injecting command
            current_lines = len(self.pty_reader.output_lines)
            
            # Update command tracking - set checkpoint BEFORE sending command
            self._command_counter += 1
            command_id = f"cmd_{self._command_counter}"
            
            self.pty_reader.set_current_command(command_id)
            
            # Send command to subprocess via PTY
            command_bytes = f"{cmd}\n".encode('utf-8')
            os.write(self.master_fd, command_bytes)
            
            logger.info(f"Injected command via PTY: {cmd}")
            return True, current_lines
            
        except Exception as e:
            logger.error(f"Failed to inject command '{cmd}': {e}")
            return False, 0
    
    async def send_signal(self, signal_char: str) -> bool:
        """Send a signal character (like Ctrl+C) to the subprocess via PTY"""
        if not self.process or self.master_fd is None:
            return False
            
        try:
            if signal_char == "SIGINT":  # Ctrl+C
                os.write(self.master_fd, b"\x03")  # ASCII 3 = Ctrl+C
                logger.info("Sent SIGINT (Ctrl+C) to subprocess")
                return True
            elif signal_char == "SIGTERM":  # Ctrl+\
                os.write(self.master_fd, b"\x1c")  # ASCII 28 = Ctrl+\
                logger.info("Sent SIGTERM (Ctrl+\\) to subprocess")
                return True
            else:
                logger.error(f"Unknown signal: {signal_char}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send signal '{signal_char}': {e}")
            return False
    
    def get_interleaved_output(self, count: int, stream_filter: str = "both") -> List[dict]:
        """Get output from PTY (all streams combined)"""
        # PTY combines all streams, so stream_filter is ignored
        all_lines = self.pty_reader.get_recent_lines(count)
        
        # Convert to dict format
        return [
            {
                "cmd": line.cmd,
                "timestamp": line.timestamp.isoformat(),
                "text": line.text,
                "stream": line.stream
            }
            for line in all_lines
        ]
    
    async def stop_process(self):
        """Stop the subprocess and PTY reader with proper SIGTERM -> SIGKILL sequence"""
        if self.process:
            try:
                # First try SIGTERM (graceful)
                self.process.terminate()
                logger.info("Sent SIGTERM to subprocess")
                
                # Wait up to 5 seconds for graceful shutdown
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=5.0)
                    logger.info("Subprocess terminated gracefully")
                except asyncio.TimeoutError:
                    # Force kill with SIGKILL
                    logger.info("Subprocess didn't terminate gracefully, sending SIGKILL")
                    self.process.kill()
                    await self.process.wait()
                    logger.info("Subprocess killed forcefully")
                    
            except Exception as e:
                logger.error(f"Error stopping subprocess: {e}")
            
        await self.pty_reader.stop()
        logger.info("Subprocess and PTY reader stopped")
    
    def is_running(self) -> bool:
        """Check if subprocess is running"""
        return self.process is not None and self.process.returncode is None

def create_subprocess_plugin(server_name: str = "Subprocess Manager") -> FastMCP:
    """Create the clean 3-tool subprocess manager MCP plugin"""
    
    # Create global subprocess manager
    subprocess_manager = SubprocessManager()
    
    # Create MCP server
    mcp = FastMCP(server_name)

    @mcp.tool
    async def start(command: str, ctx: Context) -> str:
        """Start a subprocess with the given command"""
        await ctx.info(f"Starting subprocess: {command}")
        
        if subprocess_manager.is_running():
            return "ERROR: A subprocess is already running. Stop it first."
        
        cmd_parts = command.split()
        success = await subprocess_manager.start_process(cmd_parts)
        
        if success:
            return f"Successfully started subprocess: {command}"
        else:
            return f"Failed to start subprocess: {command}"

    @mcp.tool
    async def run(
        ctx: Context, 
        command: str, 
        tail_count: int = 10, 
        stream: Literal["stdout", "stderr", "both"] = "both"
    ) -> str:
        """Inject a command into the subprocess and tail the output from that command"""
        await ctx.info(f"Running command: {command} (tail {stream})")
        
        if not subprocess_manager.is_running():
            return "ERROR: No subprocess is currently running. Start one first."
        
        # Inject the command - this sets the command checkpoint in PipeReaders
        success, _ = await subprocess_manager.inject_command(command)
        
        if not success:
            return "ERROR: Failed to inject command"
        
        # Wait for command output to appear
        await asyncio.sleep(0.5)
        
        # Get output from current command only - this is what a real terminal shows for THIS command
        all_lines = subprocess_manager.pty_reader.get_current_command_output()
        
        # Convert to dict format
        output_lines = [
            {
                "cmd": line.cmd,
                "timestamp": line.timestamp.isoformat(),
                "text": line.text,
                "stream": line.stream
            }
            for line in all_lines
        ]
        
        if not output_lines:
            return f"Command injected successfully. No output from this command yet."
        
        # Format output - show only output from this command execution
        result = f"Command injected successfully. Current command output:\n"
        for line in output_lines:
            result += f"{line['text']}\n"
        
        return result.rstrip()

    @mcp.tool
    async def tail(
        ctx: Context, 
        count: int = 10, 
        stream: Literal["stdout", "stderr", "both"] = "both"
    ) -> str:
        """Tail the output from the subprocess"""
        await ctx.info(f"Tailing {stream} output ({count} lines)")
        
        if not subprocess_manager.is_running():
            return "ERROR: No subprocess is currently running."
        
        # Get interleaved output
        output_lines = subprocess_manager.get_interleaved_output(count, stream)
        
        if not output_lines:
            return f"No {stream} output available yet."
        
        # Format output
        result = f"Recent {stream} output ({len(output_lines)} lines):\n\n"
        for line in output_lines:
            stream_marker = f"[{line['stream']}]" if stream == "both" else ""
            result += f"{stream_marker} {line['text']}\n"
        
        return result.rstrip()

    @mcp.tool
    async def signal(ctx: Context, signal_name: str) -> str:
        """Send a signal to the subprocess (SIGINT, SIGTERM)"""
        await ctx.info(f"Sending signal {signal_name} to subprocess")
        
        if not subprocess_manager.is_running():
            return "No subprocess is currently running."
        
        success = await subprocess_manager.send_signal(signal_name)
        if success:
            return f"Signal {signal_name} sent successfully."
        else:
            return f"Failed to send signal {signal_name}."

    @mcp.tool
    async def stop(ctx: Context) -> str:
        """Stop the current subprocess"""
        await ctx.info("Stopping subprocess")
        
        if not subprocess_manager.is_running():
            return "No subprocess is currently running."
        
        await subprocess_manager.stop_process()
        return "Subprocess stopped successfully."

    return mcp
