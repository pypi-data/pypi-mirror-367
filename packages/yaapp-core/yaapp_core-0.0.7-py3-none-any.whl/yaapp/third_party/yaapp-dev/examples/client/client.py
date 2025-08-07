#!/usr/bin/env python3
"""
yaapp Framework Client - Uses yaapp's built-in client system with SSE streaming support.

This replaces the standalone client with yaapp's framework-native client approach.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from yaapp import yaapp
from yaapp.client import create_client


class YaappStreamingClient:
    """Streaming client wrapper around yaapp's built-in AppProxy."""
    
    def __init__(self, target_url: str, proxy_name: str = "remote"):
        """Initialize streaming client with yaapp framework."""
        self.target_url = target_url.rstrip('/')
        self.proxy_name = proxy_name
        
        # Create yaapp client using framework's built-in client
        self.app = create_client(target_url, proxy_name)
        self.proxy = self.app  # Use the client directly as proxy
    
    def list_functions(self) -> Dict[str, Any]:
        """List available functions using framework client."""
        return {"functions": self.proxy.list_functions()}
    
    def call_function(self, function_name: str, **kwargs) -> Any:
        """Call function using framework's AppProxy."""
        return self.proxy.execute_command(function_name, [f"--{k}={v}" for k, v in kwargs.items()])
    
    async def call_function_async(self, function_name: str, **kwargs) -> Any:
        """Async function call using framework's AppProxy."""
        # For now, wrap the sync call in an async context
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: self.proxy.execute_command(function_name, [f"--{k}={v}" for k, v in kwargs.items()])
        )
    
    def stream_sse(self, function_name: str, **kwargs):
        """Stream from SSE endpoint using POST request with JSON body."""
        try:
            import httpx
        except ImportError:
            print("❌ httpx required for streaming. Install with: pip install httpx")
            return
        
        import json
        
        # Construct SSE endpoint URL
        url = f"{self.target_url}/{function_name}/stream"
        
        print(f"🔗 Streaming from: {url}")
        
        try:
            with httpx.Client() as client:
                with client.stream("POST", url, json=kwargs) as response:
                    if response.status_code != 200:
                        print(f"❌ HTTP {response.status_code}")
                        return
                    
                    print("📡 Connected to SSE stream")
                    
                    for line in response.iter_lines():
                        if line.startswith('data: '):
                            data = line[6:]  # Remove 'data: ' prefix
                            try:
                                parsed = json.loads(data)
                                yield parsed
                            except json.JSONDecodeError:
                                yield {"raw": data}
                        
                        elif line.startswith('event: error'):
                            print("❌ Stream error")
                            break
                            
                    print("🔚 Stream ended")
                
        except Exception as e:
            print(f"❌ Stream error: {e}")
    
    def health_check(self) -> bool:
        """Check if server is responding using framework client."""
        try:
            # Try to get function list as health check
            functions = self.list_functions()
            return isinstance(functions, dict)
        except Exception:
            return False


def print_colored(text: str, color: str = ""):
    """Print colored text to terminal."""
    colors = {
        "red": "\033[0;31m",
        "green": "\033[0;32m", 
        "yellow": "\033[1;33m",
        "blue": "\033[0;34m",
        "reset": "\033[0m"
    }
    
    if color in colors:
        print(f"{colors[color]}{text}{colors['reset']}")
    else:
        print(text)


def pretty_print_json(data: Dict[str, Any]):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def list_command(client: YaappStreamingClient):
    """Handle list command."""
    print_colored(f"Fetching available functions from {client.target_url}...", "blue")
    print()
    
    try:
        functions = client.list_functions()
        print_colored("Available functions:", "green")
        pretty_print_json(functions)
    except Exception as e:
        print_colored(f"Error: {e}", "red")
        print("Make sure the yaapp server is running.")
        sys.exit(1)


def call_command(client: YaappStreamingClient, function_name: str, args: Dict[str, str]):
    """Handle call command."""
    print_colored(f"Calling function '{function_name}' on {client.target_url}...", "blue")
    
    # Convert string arguments to appropriate types
    converted_args = {}
    for key, value in args.items():
        # Try to convert common types
        if value.lower() in ('true', 'false'):
            converted_args[key] = value.lower() == 'true'
        elif value.isdigit():
            converted_args[key] = int(value)
        elif '.' in value and value.replace('.', '').isdigit():
            converted_args[key] = float(value)
        else:
            converted_args[key] = value
    
    try:
        result = client.call_function(function_name, **converted_args)
        print_colored("Response:", "green")
        pretty_print_json(result if isinstance(result, dict) else {"result": result})
    except Exception as e:
        print_colored(f"Error: {e}", "red")
        print(f"Check if function '{function_name}' exists and the server is running.")
        sys.exit(1)


def stream_command(client: YaappStreamingClient, function_name: str, args: Dict[str, str]):
    """Handle stream command."""
    print_colored(f"Streaming from '{function_name}' on {client.target_url}...", "blue")
    print("Press Ctrl+C to stop streaming")
    print()
    
    # Convert string arguments to appropriate types
    converted_args = {}
    for key, value in args.items():
        if value.lower() in ('true', 'false'):
            converted_args[key] = value.lower() == 'true'
        elif value.isdigit():
            converted_args[key] = int(value)
        elif '.' in value and value.replace('.', '').isdigit():
            converted_args[key] = float(value)
        else:
            converted_args[key] = value
    
    try:
        for event in client.stream_sse(function_name, **converted_args):
            print_colored(f"📊 {event}", "")
    except KeyboardInterrupt:
        print_colored("\n👋 Streaming stopped by user", "yellow")
    except Exception as e:
        print_colored(f"Error: {e}", "red")
        print(f"Check if function '{function_name}' has streaming support.")
        sys.exit(1)


def health_command(client: YaappStreamingClient):
    """Handle health check command."""
    print_colored(f"Checking server health at {client.target_url}...", "blue")
    
    if client.health_check():
        print_colored("✓ Server is responding", "green")
    else:
        print_colored("✗ Server is not responding", "red")
        sys.exit(1)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="yaapp Framework Client with SSE streaming support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list
  %(prog)s call greet
  %(prog)s call greet name=Alice formal=true
  %(prog)s stream auto_counter end=5
  %(prog)s stream simulate_progress steps=3
  %(prog)s -H api.example.com -p 9000 list
  %(prog)s health

Environment variables:
  YAAPP_HOST    Server host (default: localhost)
  YAAPP_PORT    Server port (default: 8000)
        """
    )
    
    # Server options
    parser.add_argument(
        "-H", "--host", 
        default=os.getenv("YAAPP_HOST", "localhost"),
        help="Server host (default: localhost)"
    )
    parser.add_argument(
        "-p", "--port", 
        type=int,
        default=int(os.getenv("YAAPP_PORT", "8000")),
        help="Server port (default: 8000)"
    )
    parser.add_argument(
        "--proxy-name",
        default="remote",
        help="Name for the remote proxy (default: remote)"
    )
    
    # Commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    subparsers.add_parser("list", help="List all available functions")
    
    # Call command
    call_parser = subparsers.add_parser("call", help="Call a function")
    call_parser.add_argument("function", help="Function name to call")
    call_parser.add_argument(
        "args", 
        nargs="*", 
        help="Function arguments in key=value format"
    )
    
    # Stream command
    stream_parser = subparsers.add_parser("stream", help="Stream from a function")
    stream_parser.add_argument("function", help="Function name to stream from")
    stream_parser.add_argument(
        "args", 
        nargs="*", 
        help="Function arguments in key=value format"
    )
    
    # Health command
    subparsers.add_parser("health", help="Check server health")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Create yaapp framework client
    target_url = f"http://{args.host}:{args.port}"
    client = YaappStreamingClient(target_url, args.proxy_name)
    
    # Handle commands
    if args.command == "list":
        list_command(client)
    
    elif args.command == "call":
        # Parse key=value arguments
        call_args = {}
        for arg in args.args:
            if "=" in arg:
                key, value = arg.split("=", 1)
                call_args[key] = value
            else:
                print_colored(f"Warning: Ignoring argument '{arg}' (expected key=value format)", "yellow")
        
        call_command(client, args.function, call_args)
    
    elif args.command == "stream":
        # Parse key=value arguments
        stream_args = {}
        for arg in args.args:
            if "=" in arg:
                key, value = arg.split("=", 1)
                stream_args[key] = value
            else:
                print_colored(f"Warning: Ignoring argument '{arg}' (expected key=value format)", "yellow")
        
        stream_command(client, args.function, stream_args)
    
    elif args.command == "health":
        health_command(client)


if __name__ == "__main__":
    import os
    main()