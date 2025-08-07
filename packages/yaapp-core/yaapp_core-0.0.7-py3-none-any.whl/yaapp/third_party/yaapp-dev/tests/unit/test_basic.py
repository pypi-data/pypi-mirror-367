#!/usr/bin/env python3
"""
Basic test of YApp functionality without external dependencies
"""

import os
import sys

# Add src to path so we can import yaapp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


# Mock click for testing
class MockClick:
    def __init__(self):
        pass

    def group(self, invoke_without_command=True):
        def decorator(func):
            func._is_group = True
            return func

        return decorator

    def command(self):
        def decorator(func):
            func._is_command = True
            return func

        return decorator

    def option(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def argument(self, *args, **kwargs):
        def decorator(func):
            return func

        return decorator

    def pass_context(self):
        def decorator(func):
            return func

        return decorator

    def echo(self, message):
        print(message)

    def Choice(self, choices):
        return str


# Mock click module
sys.modules["click"] = MockClick()

try:
    from yaapp import Yaapp

    # Test basic functionality
    print("Testing YApp basic functionality...")

    # Create instance
    yapp = Yaapp()
    print("✓ YApp instance created")

    # Test decorator usage
    @yaapp.expose
    def test_func(name: str) -> str:
        return f"Hello, {name}!"

    print("✓ Function exposed via decorator")

    # Test method call usage
    yaapp.expose({"math": {"add": lambda x, y: x + y, "subtract": lambda x, y: x - y}})
    print("✓ Functions exposed via method call")

    # Check registry
    print(f"✓ Registry contains: {list(yaapp._registry.keys())}")

    # Test list functions (should work without click)
    print("\nTesting _list_functions:")
    yaapp._list_functions()

    print("\n✅ All basic tests passed!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
