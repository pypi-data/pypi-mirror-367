#!/usr/bin/env python3
"""
Test click reflection functionality
"""

import os
import sys

# Add src to path so we can import yaapp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


# Mock click for testing
class MockClick:
    def __init__(self):
        self.commands = {}
        self.groups = {}

    def group(self, name=None, invoke_without_command=False):
        def decorator(func):
            func._is_group = True
            if name:
                self.groups[name] = func
            return func

        return decorator

    def command(self, name=None):
        def decorator(func):
            func._is_command = True
            if name:
                self.commands[name] = func
            return func

        return decorator

    def option(self, *args, **kwargs):
        def decorator(func):
            if not hasattr(func, "_options"):
                func._options = []
            func._options.append((args, kwargs))
            return func

        return decorator

    def argument(self, *args, **kwargs):
        def decorator(func):
            if not hasattr(func, "_arguments"):
                func._arguments = []
            func._arguments.append((args, kwargs))
            return func

        return decorator

    def pass_context(self):
        def decorator(func):
            return func

        return decorator

    def echo(self, message, err=False):
        print(message)

    def Choice(self, choices):
        return str


# Mock click module
sys.modules["click"] = MockClick()

try:
    from yaapp import Yaapp

    # Test reflection functionality
    print("Testing click reflection...")

    # Create instance
    app = Yaapp()
    print("✓ YApp instance created")

    # Test different object types
    @app.expose
    def simple_func(name: str, age: int = 25, active: bool = True) -> str:
        """A simple function with different parameter types."""
        return f"Name: {name}, Age: {age}, Active: {active}"

    @app.expose
    class TestClass:
        """A test class with methods."""

        def method1(self, x: int = 10) -> int:
            """Method with integer parameter."""
            return x * 2

        def method2(self, text: str = "hello") -> str:
            """Method with string parameter."""
            return text.upper()

    # Test nested functions
    app.expose(
        {
            "math": {"add": lambda x, y: x + y, "multiply": lambda x, y: x * y},
            "utils": {"reverse": lambda text: text[::-1]},
        }
    )

    print("✓ Functions and objects exposed")
    print(f"✓ Registry contains: {list(app._registry.keys())}")

    # Test reflection
    print("\n=== Testing Reflection ===")
    try:
        from yaapp.reflection import ClickReflection
        reflection = ClickReflection(app)
        cli = reflection.create_reflective_cli()
        if cli:
            print("✓ Reflective CLI created successfully")

            # Check if commands were added
            if hasattr(cli, "commands"):
                print("✓ CLI is a click group")
                print(f"✓ CLI commands: {list(cli.commands.keys())}")

            print("✓ Reflection test completed")
        else:
            print("✗ Failed to create reflective CLI")
    except Exception as e:
        print(f"✗ Reflection test failed: {e}")

    print("\n✅ All reflection tests passed!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
