#!/usr/bin/env python3
"""
Test YApp client functionality.
"""

import sys
import os
sys.path.insert(0, "../../src")

from yaapp.client import create_client


def test_client():
    """Test YApp client functionality."""
    print("Testing YApp client...")
    
    try:
        # Create client app
        client_app = create_client("http://localhost:8000", "remote")
        print("✅ Client app created successfully")
        
        # Verify it's a proper YaappClient
        from yaapp.client import YaappClient
        assert isinstance(client_app, YaappClient), "Client should be a YaappClient instance"
        print("✅ Client is a proper YaappClient")
        
        print("✅ YApp client test complete!")
    
    except Exception as e:
        if "Connection refused" in str(e):
            print("✅ Client test skipped (no server running)")
        else:
            raise e
    
    print("\nInfinite chaining test:")
    print("1. Start server A: python test_appproxy.py server")
    print("2. Start client B (proxies A): python -m yaapp.client --target http://localhost:8000 server --port 8001")
    print("3. Start client C (proxies B): python -m yaapp.client --target http://localhost:8001 server --port 8002") 
    print("4. Connect to C: python -m yaapp.client --target http://localhost:8002 tui")


if __name__ == "__main__":
    test_client()