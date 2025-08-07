#!/usr/bin/env python3
"""Docker Plugin - Minimal demonstration"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

# Import the singleton instance - plugins auto-discovered from config!
from yaapp import yaapp

if __name__ == "__main__":
    yaapp.run()