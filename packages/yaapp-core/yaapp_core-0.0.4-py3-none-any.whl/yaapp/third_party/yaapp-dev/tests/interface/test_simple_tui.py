#!/usr/bin/env python3
"""
Test simple TUI functionality without external dependencies
"""

import os
import sys

# Add src to path so we can import yaapp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from yaapp import Yaapp

# Create instance
app = Yaapp()


# Add test functions
@app.expose
def greet(name: str = "World") -> str:
    """Greet someone."""
    return f"Hello, {name}!"


@app.expose
def add(x: int = 0, y: int = 0) -> int:
    """Add two numbers."""
    return x + y


# Test the TUI command execution
print("Testing TUI command execution...")

# Test simple command execution
try:
    result = app._call_function_with_args(app._registry["greet"][0], ["--name=Alice"])
    print(f"✓ greet with --name=Alice: {result}")
except Exception as e:
    print(f"✗ Error with greet: {e}")

try:
    result = app._call_function_with_args(app._registry["add"][0], ["--x=5", "--y=3"])
    print(f"✓ add with --x=5 --y=3: {result}")
except Exception as e:
    print(f"✗ Error with add: {e}")

# Test TUI execution
print("\n=== Testing TUI execution ===")
try:
    app._execute_tui_command("greet --name=Bob")
    print("✓ TUI command execution works")
except Exception as e:
    print(f"✗ TUI execution error: {e}")

print("\n✅ TUI functionality test completed!")
print("Available backends:", ["typer", "prompt", "rich", "click"])
print("To test interactively, run this script and uncomment the TUI line below:")
print("# app._run_tui('typer')")
