#!/usr/bin/env python3
"""
YAPP Generic Proxy Client - Plugin-based client that loads AppProxy plugin.

This is the generic client that demonstrates the plugin architecture:
1. AppProxy is a PLUGIN that implements CustomExposer interface
2. CustomExposer is the CORE extensibility mechanism
3. This is ONE GENERIC CLIENT that uses the AppProxy plugin

Usage:
  python proxy_client.py --target http://api.example.com:8000 tui
  python proxy_client.py --target http://api.example.com:8000 server --port 9000
  python proxy_client.py --target http://api.example.com:8000 run remote.greet --name Alice
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from yaapp import Yaapp
from yaapp.plugins import AppProxy


def create_proxy_app(target_url: str, app_name: str = None) -> YApp:
    """Create a YApp that proxies to a remote YApp server using the AppProxy plugin.
    
    This demonstrates the plugin architecture:
    1. AppProxy is a plugin that implements CustomExposer interface
    2. We expose it with custom=True to use the CustomExposer
    3. AppProxy discovers remote functions and exposes them locally
    4. The result is a full YAPP app that can use any runner
    """
    # Create the generic YAPP application
    proxy_name = app_name or f"YAPP Proxy -> {target_url}"
    app = Yaapp()
    
    print(f"🚀 Creating YAPP Proxy Client: {proxy_name}")
    print(f"🎯 Target: {target_url}")
    print(f"🔌 Loading AppProxy plugin...")
    
    # Create AppProxy plugin instance
    proxy = AppProxy(target_url)
    
    # Expose the proxy using custom=True (this triggers CustomExposer)
    # The CustomExposer will call proxy.expose_to_registry() and proxy.execute_call()
    app.expose(proxy, name="remote", custom=True)
    
    print(f"✅ AppProxy plugin loaded successfully!")
    print(f"🎮 You can now use any YAPP runner: tui, server, run, list")
    
    return app


def main():
    """Main entry point for the generic YAPP proxy client.
    
    This demonstrates the plugin architecture:
    - ONE generic client that loads the AppProxy plugin
    - AppProxy implements CustomExposer interface
    - Can use ANY YAPP runner (TUI, server, CLI)
    - Enables service chaining and composition
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="YAPP Generic Proxy Client - Plugin-based client using AppProxy plugin",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Plugin Architecture:
  This is a generic client that loads the AppProxy plugin to connect to remote YAPP servers.
  The AppProxy plugin implements the CustomExposer interface for extensibility.

Examples:
  # Interactive TUI mode
  %(prog)s --target http://localhost:8000 tui
  %(prog)s --target http://localhost:8000 tui --backend rich
  
  # Start as server (enables chaining)
  %(prog)s --target http://api.example.com:8000 server --port 9000
  
  # Direct function execution
  %(prog)s --target http://localhost:8000 run remote.greet --name Alice
  %(prog)s --target http://localhost:8000 run remote.Calculator.add --x 5 --y 3
  
  # List available functions
  %(prog)s --target http://localhost:8000 list
  
  # Service chaining example:
  # Server A (port 8000) ←→ Proxy B (port 9000) ←→ Proxy C (port 10000)
  %(prog)s --target http://localhost:8000 server --port 9000
        """
    )
    
    parser.add_argument(
        "--target", 
        required=True,
        help="Target YApp server URL (e.g., http://localhost:8000)"
    )
    
    parser.add_argument(
        "--name",
        help="Optional name for the proxy application"
    )
    
    # Parse known args to get target, then let YApp handle the rest
    args, remaining = parser.parse_known_args()
    
    print("=" * 60)
    print("🔌 YAPP Generic Proxy Client - Plugin Architecture Demo")
    print("=" * 60)
    
    try:
        # Create proxy app using the AppProxy plugin
        app = create_proxy_app(args.target, args.name)
        
        # Add remaining args back to sys.argv for YApp to process
        sys.argv = [sys.argv[0]] + remaining
        
        print("\n" + "=" * 60)
        print("🎮 Starting YAPP application with discovered remote functions...")
        print("=" * 60)
        
        # Run the proxy app with standard YApp functionality
        # This can use ANY YAPP runner: tui, server, run, list
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Proxy client stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure the target server is running and accessible")
        sys.exit(1)


if __name__ == "__main__":
    main()