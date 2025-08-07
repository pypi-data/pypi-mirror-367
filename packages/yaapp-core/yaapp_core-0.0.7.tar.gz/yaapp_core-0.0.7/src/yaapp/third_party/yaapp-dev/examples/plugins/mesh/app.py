#!/usr/bin/env python3
"""
Mesh Plugin Example - Service/Plugin Orchestrator

This example demonstrates the Mesh plugin for orchestrating and managing
multiple services/plugins.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp.app import Yaapp

def main():
    """Run the Mesh example."""
    app = Yaapp()
    app.run()

if __name__ == "__main__":
    main()