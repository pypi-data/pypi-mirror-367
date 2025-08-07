#!/usr/bin/env python3
"""
Registry Plugin Example - Service Registry for Microservices

This example demonstrates the Registry plugin for service discovery
in a microservices architecture.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp.app import Yaapp

def main():
    """Run the Registry example."""
    app = Yaapp()
    app.run()

if __name__ == "__main__":
    main()