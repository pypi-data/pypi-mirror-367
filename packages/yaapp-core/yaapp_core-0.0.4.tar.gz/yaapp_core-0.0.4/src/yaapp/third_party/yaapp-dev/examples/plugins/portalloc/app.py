#!/usr/bin/env python3
"""
PortAlloc Plugin Example - Microservice Port Allocation Manager

This example demonstrates the PortAlloc plugin for managing port allocations
for microservices.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp.app import Yaapp

def main():
    """Run the PortAlloc example."""
    app = Yaapp()
    app.run()

if __name__ == "__main__":
    main()