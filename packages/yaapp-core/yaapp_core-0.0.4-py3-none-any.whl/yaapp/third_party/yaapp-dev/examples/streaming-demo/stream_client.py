#!/usr/bin/env python3
"""
Enhanced yaapp streaming client using framework's built-in client system.

Demonstrates both regular function calls and SSE streaming using yaapp's native client.
"""

import json
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Import the framework client
sys.path.insert(0, str(Path(__file__).parent.parent / "client"))
from client import YaappStreamingClient, print_colored


def main():
    """Test streaming endpoints using yaapp framework client."""
    client = YaappStreamingClient("http://localhost:8000")
    
    print_colored("🚀 yaapp Framework Streaming Client", "green")
    print_colored(f"Server: {client.target_url}", "blue")
    print()
    
    # Test 1: Regular function endpoint
    print_colored("Testing regular endpoint:", "yellow")
    try:
        result = client.call_function("regular_function", message="Hello from framework client")
        print_colored(f"✓ Regular call: {result}", "green")
    except Exception as e:
        print_colored(f"❌ Regular call failed: {e}", "red")
    
    print()
    
    # Test 2: List available functions
    print_colored("Available functions:", "yellow")
    try:
        functions = client.list_functions()
        if functions:
            for func_name, func_info in functions.items():
                print_colored(f"  📋 {func_name}", "blue")
        else:
            print_colored("  No functions discovered yet", "yellow")
    except Exception as e:
        print_colored(f"❌ Function listing failed: {e}", "red")
    
    print()
    
    # Test 3: Stream from auto_counter endpoint
    print_colored("Streaming from auto_counter (5 events):", "yellow")
    try:
        event_count = 0
        for event in client.stream_sse("auto_counter", end=4):  # 0-4 = 5 events
            print_colored(f"📊 Counter: {event}", "")
            event_count += 1
            if event_count >= 5:  # Limit for demo
                break
        print_colored("✓ Counter stream completed", "green")
    except KeyboardInterrupt:
        print_colored("\n👋 Counter streaming stopped by user", "yellow")
    except Exception as e:
        print_colored(f"❌ Counter streaming error: {e}", "red")
    
    print()
    
    # Test 4: Stream from progress simulation
    print_colored("Streaming from simulate_progress (3 steps):", "yellow")
    try:
        for event in client.stream_sse("simulate_progress", steps=2):  # Quick demo
            print_colored(f"📊 Progress: {event}", "")
        print_colored("✓ Progress stream completed", "green")
    except KeyboardInterrupt:
        print_colored("\n👋 Progress streaming stopped by user", "yellow")
    except Exception as e:
        print_colored(f"❌ Progress streaming error: {e}", "red")


if __name__ == "__main__":
    print("Make sure to start the streaming demo server first:")
    print("  python examples/streaming-demo/app.py server")
    print()
    
    try:
        main()
    except Exception as e:
        print_colored(f"\n❌ Client error: {e}", "red")
        print("Make sure the streaming demo server is running on localhost:8000")
        sys.exit(1)