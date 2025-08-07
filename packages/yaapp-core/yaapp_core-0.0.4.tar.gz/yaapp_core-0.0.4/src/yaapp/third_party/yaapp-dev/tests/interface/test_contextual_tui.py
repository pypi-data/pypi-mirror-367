#!/usr/bin/env python3
"""
Test contextual TUI functionality
"""

import inspect
import os
import sys

# Add src to path so we can import yaapp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from yaapp import Yaapp

# Create instance
app = Yaapp()


# Add test functions and objects to demonstrate contextual navigation
@app.expose
def greet(name: str = "World", formal: bool = False) -> str:
    """Greet someone."""
    greeting = "Good day" if formal else "Hello"
    return f"{greeting}, {name}!"


@app.expose
class Calculator:
    """A calculator with mathematical operations."""

    def add(self, x: float = 0.0, y: float = 0.0) -> float:
        """Add two numbers."""
        return x + y

    def multiply(self, x: float = 1.0, y: float = 1.0) -> float:
        """Multiply two numbers."""
        return x * y


# Add nested functions to demonstrate hierarchical navigation
app.expose(
    {
        "math": {
            "basic": {"add": lambda x, y: x + y, "subtract": lambda x, y: x - y},
            "advanced": {"power": lambda x, y: x**y, "sqrt": lambda x: x**0.5},
        },
        "string": {
            "transform": {
                "upper": lambda text: text.upper(),
                "lower": lambda text: text.lower(),
                "reverse": lambda text: text[::-1],
            },
            "analyze": {
                "length": lambda text: len(text),
                "words": lambda text: len(text.split()),
            },
        },
    }
)

print("=== Contextual TUI Test ===")
print(f"App name: {app._get_app_name()}")
print(f"Registry items: {len(app._registry)}")
print()

# Show registry structure
print("Registry structure:")
for name in sorted(app._registry.keys()):
    obj = app._registry[name][0]
    obj_type = "function"
    if inspect.isclass(obj):
        obj_type = "class"
    print(f"  {name:<25} | {obj_type}")

print()
print("Expected navigation structure:")
print("Root:")
print("  ├── greet (function)")
print("  ├── Calculator (class) → navigate to Calculator context")
print("  ├── math (namespace) → navigate to math context")
print("  │   ├── basic (namespace) → navigate to math:basic context")
print("  │   │   ├── add (function)")
print("  │   │   └── subtract (function)")
print("  │   └── advanced (namespace)")
print("  │       ├── power (function)")
print("  │       └── sqrt (function)")
print("  └── string (namespace)")
print("      ├── transform (namespace)")
print("      │   ├── upper (function)")
print("      │   ├── lower (function)")
print("      │   └── reverse (function)")
print("      └── analyze (namespace)")
print("          ├── length (function)")
print("          └── words (function)")

print()
print("To test interactively:")
print("1. Uncomment the line below:")
print("# app._run_tui('typer')")
print()
print("2. Expected TUI behavior:")
print("   - Start at root context with prompt 'test_contextual_tui>'")
print(
    "   - Type 'math' to enter math context → prompt becomes 'test_contextual_tui:math>'"
)
print(
    "   - Type 'basic' to enter basic context → prompt becomes 'test_contextual_tui:math:basic>'"
)
print("   - Type 'add --x=5 --y=3' to execute function")
print("   - Type 'back' or '..' to go back to parent context")
print("   - Type 'help' to see available commands in current context")
print("   - Type 'list' to see available commands")

# Uncomment to test interactively:
# app._run_tui('typer')
