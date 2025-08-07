#!/usr/bin/env python3
"""
Test TUI functionality
"""

import os
import sys

# Add src to path so we can import yaapp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from yaapp import Yaapp

# Create instance
app = Yaapp()


# Add some test functions
@app.expose
def greet(name: str, formal: bool = False) -> str:
    """Greet a person."""
    greeting = "Good day" if formal else "Hello"
    return f"{greeting}, {name}!"


@app.expose
class Calculator:
    """A simple calculator class."""

    def add(self, x: int = 0, y: int = 0) -> int:
        """Add two numbers."""
        return x + y

    def multiply(self, x: int = 1, y: int = 1) -> int:
        """Multiply two numbers."""
        return x * y


# Add nested functions
app.expose({"math": {"power": lambda x, y: x**y, "sqrt": lambda x: x**0.5}})

print("Testing TUI backends...")
print("Available functions:", list(app._registry.keys()))

# Test typer backend (simplest - no dependencies)
print("\n=== Testing Typer Backend ===")
print("This would start the typer TUI...")
# app._run_tui("typer")  # Uncomment to test interactively

print("\n=== Registry Contents ===")
for name, obj in app._registry.items():
    print(f"  {name}: {type(obj)} - {obj}")

print("\n✅ TUI setup completed!")
print(
    "To test interactively, run: python examples/data-analyzer/app.py tui --backend typer"
)
