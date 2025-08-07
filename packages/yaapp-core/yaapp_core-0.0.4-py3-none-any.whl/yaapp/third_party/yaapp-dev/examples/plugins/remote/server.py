#!/usr/bin/env python3
"""Remote Process Plugin - Server"""

# Add src directory to path
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

# Import yaapp and the plugin
from yaapp import yaapp

if __name__ == "__main__":
    # Use yaapp's built-in CLI system - it already handles server command!
    yaapp.run()
