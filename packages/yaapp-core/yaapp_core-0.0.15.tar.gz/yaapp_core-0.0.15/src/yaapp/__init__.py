"""
Yaapp - Clean library interface.

Main exports for library users.
"""

from .expose import expose
from .result import Ok, Result
from .yaapp import Yaapp

# Version info
__version__ = "0.0.15"

# Main library exports
__all__ = ["Yaapp", "Result", "Ok", "expose", "__version__"]


def main():
    """Main entry point for the yaapp CLI command."""
    Yaapp().run("click")

