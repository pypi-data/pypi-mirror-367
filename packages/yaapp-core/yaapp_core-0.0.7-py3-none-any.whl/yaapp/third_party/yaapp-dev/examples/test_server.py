#!/usr/bin/env python3
"""
Test YAPP server for demonstrating the AppProxy plugin system.

This server exposes some simple functions that can be discovered and proxied
by the generic proxy client using the AppProxy plugin.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yaapp import Yaapp


def create_test_server() -> YApp:
    """Create a test YAPP server with various functions to proxy."""
    app = Yaapp()
    
    # Simple function
    @app.expose
    def greet(name: str, formal: bool = False) -> str:
        """Greet a person."""
        greeting = "Good day" if formal else "Hello"
        return f"{greeting}, {name}!"
    
    # Class with methods
    @app.expose
    class Calculator:
        """A simple calculator."""
        
        def add(self, x: int, y: int) -> int:
            """Add two numbers."""
            return x + y
        
        def multiply(self, x: int, y: int) -> int:
            """Multiply two numbers."""
            return x * y
        
        def divide(self, x: float, y: float) -> float:
            """Divide two numbers."""
            if y == 0:
                raise ValueError("Cannot divide by zero")
            return x / y
    
    # Dictionary tree of functions
    def subtract(x: int, y: int) -> int:
        """Subtract two numbers."""
        return x - y
    
    def power(x: int, y: int) -> int:
        """Raise x to the power of y."""
        return x ** y
    
    app.expose({
        "math": {
            "basic": {
                "subtract": subtract,
                "power": power
            },
            "constants": {
                "pi": lambda: 3.14159,
                "e": lambda: 2.71828
            }
        },
        "utils": {
            "reverse": lambda s: s[::-1],
            "upper": lambda s: s.upper(),
            "length": lambda s: len(s)
        }
    })
    
    return app


def main():
    """Main entry point for test server."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test YAPP server for AppProxy plugin demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start server on default port 8000
  %(prog)s
  
  # Start server on custom port
  %(prog)s --port 8001
  
  # Test with proxy client:
  python proxy_client.py --target http://localhost:8000 list
  python proxy_client.py --target http://localhost:8000 tui
        """
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to run the server on (default: 8000)"
    )
    
    parser.add_argument(
        "--host",
        default="localhost", 
        help="Host to bind to (default: localhost)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🧪 YAPP Test Server - AppProxy Plugin Demo")
    print("=" * 60)
    
    # Create test server
    app = create_test_server()
    
    print(f"🚀 Starting test server on http://{args.host}:{args.port}")
    print("📚 Available functions:")
    print("   • greet(name, formal=False)")
    print("   • Calculator.add(x, y)")
    print("   • Calculator.multiply(x, y)")
    print("   • Calculator.divide(x, y)")
    print("   • math.basic.subtract(x, y)")
    print("   • math.basic.power(x, y)")
    print("   • math.constants.pi()")
    print("   • math.constants.e()")
    print("   • utils.reverse(s)")
    print("   • utils.upper(s)")
    print("   • utils.length(s)")
    print()
    print("🔌 Test with proxy client:")
    print(f"   python proxy_client.py --target http://{args.host}:{args.port} list")
    print(f"   python proxy_client.py --target http://{args.host}:{args.port} tui")
    print()
    
    # Override sys.argv to pass server arguments
    sys.argv = [sys.argv[0], "server", "--host", args.host, "--port", str(args.port)]
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Test server stopped")


if __name__ == "__main__":
    main()