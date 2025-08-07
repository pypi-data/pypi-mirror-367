"""
Test configuration helper - provides proper imports without sys.path manipulation.
Import this at the top of test files instead of using sys.path.insert().
"""

import sys
from pathlib import Path

# Add src directory to Python path
_src_path = Path(__file__).parent / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

# Re-export commonly used modules for convenience
from yaapp import Yaapp
from yaapp.core import YaappCore

__all__ = ['Yaapp', 'YaappCore']