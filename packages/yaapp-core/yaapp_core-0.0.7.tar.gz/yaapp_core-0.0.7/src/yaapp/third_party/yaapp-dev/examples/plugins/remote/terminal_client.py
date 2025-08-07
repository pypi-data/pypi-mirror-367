#!/usr/bin/env python3
"""
Real-time Interactive Remote Process Client

This client provides true bidirectional terminal experience:
- Puts terminal in raw mode
- Reads character by character and sends immediately
- Streams output in real-time via SSE
"""

import asyncio
import json
import select
import sys
import termios
import tty
from typing import Optional

import aiohttp


class RealTimeClient:
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip("/")
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = True
        self.original_settings = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        self.restore_terminal()

    def setup_raw_terminal(self):
        """Put terminal in raw mode for character-by-character input"""
        if sys.stdin.isatty():
            self.original_settings = termios.tcgetattr(sys.stdin.fileno())
            tty.setraw(sys.stdin.fileno())

    def restore_terminal(self):
        """Restore terminal to original mode"""
        if self.original_settings and sys.stdin.isatty():
            termios.tcsetattr(
                sys.stdin.fileno(), termios.TCSADRAIN, self.original_settings
            )

    async def send_char(self, char: str) -> bool:
        """Send single character to remote process"""
        try:
            # Use RPC endpoint for sending input
            url = f"{self.server_url}/_rpc"
            data = {
                "function": "RemoteProcess.send_input",
                "args": {"input_text": char},
            }

            async with self.session.post(url, json=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return "error" not in result
                return False
        except Exception as e:
            print(f"\\nError sending char: {e}", file=sys.stderr)
            return False

    async def start_process_stream(self, command: str):
        """Start the remote process and return SSE stream"""
        try:
            # NOW streaming endpoints are POST with JSON body - CONSISTENT!
            url = f"{self.server_url}/start_process_stream/stream"
            data = {"command": command}

            print(f"Connecting to streaming endpoint: {url}", file=sys.stderr)
            print(f"JSON data: {data}", file=sys.stderr)

            async with self.session.post(url, json=data) as resp:
                print(f"Response status: {resp.status}", file=sys.stderr)
                if resp.status == 200:
                    print(
                        f"Successfully connected to streaming endpoint", file=sys.stderr
                    )
                    return resp
                else:
                    print(f"Error starting stream: HTTP {resp.status}", file=sys.stderr)
                    response_text = await resp.text()
                    print(f"Response: {response_text}", file=sys.stderr)
                    return None

        except Exception as e:
            print(f"Error starting process: {e}", file=sys.stderr)
            return None

    async def read_stream(self, response):
        """Read SSE stream and output to terminal"""
        try:
            async for line in response.content:
                if not self.running:
                    break

                line_str = line.decode("utf-8").strip()

                # Parse SSE format
                if line_str.startswith("data: "):
                    content = line_str[6:]  # Remove "data: " prefix

                    # Handle special messages
                    if content == "Process ended":
                        print("\\n[Process ended]")
                        self.running = False
                        break

                    # Parse JSON if it's structured data
                    try:
                        data = json.loads(content)
                        if isinstance(data, dict) and "error" in data:
                            print(f"\\nError: {data['error']}", file=sys.stderr)
                            continue
                    except json.JSONDecodeError:
                        pass

                    # Output content directly (already formatted by server)
                    print(content, end="", flush=True)

        except Exception as e:
            print(f"\\nError reading stream: {e}", file=sys.stderr)
            self.running = False

    async def read_keyboard(self):
        """Read keyboard input character by character"""
        loop = asyncio.get_event_loop()

        while self.running:
            try:
                # Check if input is available (non-blocking)
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)

                    if not char:  # EOF
                        print("\\n[EOF - exiting]")
                        self.running = False
                        break

                    # Handle special characters
                    if ord(char) == 3:  # Ctrl+C
                        print("\\n[Interrupted - exiting]")
                        self.running = False
                        break
                    elif ord(char) == 4:  # Ctrl+D
                        print("\\n[EOF - exiting]")
                        self.running = False
                        break

                    # Send character immediately to remote process
                    await self.send_char(char)

                # Small delay to prevent busy waiting
                await asyncio.sleep(0.01)

            except Exception as e:
                print(f"\\nError reading keyboard: {e}", file=sys.stderr)
                break

    async def interactive_session(self, command: str):
        """Start real-time interactive session"""
        print(f"Starting real-time session with: {command}")
        print("Press Ctrl+C or Ctrl+D to exit")
        print("-" * 50)

        # Setup raw terminal mode
        self.setup_raw_terminal()

        try:
            # Start the remote process
            response = await self.start_process_stream(command)
            if not response:
                return

            # Start both tasks concurrently
            stream_task = asyncio.create_task(self.read_stream(response))
            keyboard_task = asyncio.create_task(self.read_keyboard())

            # Wait for either task to complete
            done, pending = await asyncio.wait(
                [stream_task, keyboard_task], return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        except Exception as e:
            print(f"\\nSession error: {e}", file=sys.stderr)
        finally:
            self.running = False
            self.restore_terminal()


async def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Real-time Interactive Remote Process Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python terminal_client.py bash
  python terminal_client.py bash --server http://localhost:8000
  python terminal_client.py python3 --server http://localhost:8881
  python terminal_client.py "mysql -u root" --server http://localhost:8000
        """,
    )

    parser.add_argument("command", help="Command to run on remote server")
    parser.add_argument(
        "--server",
        default="http://localhost:8000",
        help="Server URL (default: http://localhost:8000)",
    )

    args = parser.parse_args()

    print(f"Connecting to: {args.server}")
    print(f"Command: {args.command}")
    print("Starting interactive session...")

    try:
        async with RealTimeClient(args.server) as client:
            await client.interactive_session(args.command)
    except KeyboardInterrupt:
        print("\\nInterrupted")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
