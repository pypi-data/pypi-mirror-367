#!/usr/bin/env python3
"""
Test AppProxy functionality.
"""

import sys
import os
sys.path.insert(0, "../../src")

from yaapp import Yaapp
from yaapp.plugins.app_proxy.plugin import AppProxy


def create_test_server():
    """Create a simple test server."""
    app = Yaapp()
    
    @app.expose
    def greet(name: str, formal: bool = False) -> str:
        """Greet a person."""
        greeting = "Good day" if formal else "Hello"
        return f"{greeting}, {name}!"
    
    @app.expose
    class Calculator:
        """A simple calculator."""
        def add(self, x: int, y: int) -> int:
            """Add two numbers."""
            return x + y
    
    return app


def test_appproxy():
    """Test AppProxy functionality."""
    print("Testing AppProxy plugin...")
    
    # Create test server app
    server_app = create_test_server()
    print("✅ Test server created")
    
    # Create proxy client app
    client_app = Yaapp()
    proxy = AppProxy("http://localhost:8000")  # This will fail to connect
    
    try:
        client_app.expose(proxy, name="remote", custom=True)
        print("✅ AppProxy exposed successfully (even without server)")
    except Exception as e:
        print(f"❌ AppProxy exposure failed: {e}")
    
    print("✅ AppProxy plugin test complete!")
    
    print("\nTo test with actual server:")
    print("1. In terminal 1: python test_appproxy.py server")
    print("2. In terminal 2: python examples/proxy_client.py --target http://localhost:8000 tui")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        # Start test server
        print("Starting test server on localhost:8000...")
        server_app = create_test_server()
        server_app.run_cli(["server", "--host", "localhost", "--port", "8000"])
    else:
        # Run tests
        test_appproxy()