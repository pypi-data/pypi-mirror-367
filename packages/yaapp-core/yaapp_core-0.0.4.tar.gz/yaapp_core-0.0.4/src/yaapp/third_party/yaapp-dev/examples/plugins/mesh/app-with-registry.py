#!/usr/bin/env python3
"""
Mesh + Registry Integration Example

This example demonstrates:
1. Mesh orchestrating services
2. Services automatically registering with Registry
3. Service discovery through Registry
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp.app import Yaapp

def main():
    """Run the Mesh + Registry integration example."""
    print("🚀 Starting Mesh + Registry Integration Example")
    print("   - Mesh will start and manage services")
    print("   - Services will auto-register with Registry")
    print("   - You can discover services through Registry")
    print()
    
    app = Yaapp()
    app.run()

if __name__ == "__main__":
    main()