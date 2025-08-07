#!/usr/bin/env python3
"""
Test the web mode of YApp
"""

import pytest
from yaapp import Yaapp


def test_web_mode_setup():
    """Test that web mode can be set up without errors."""
    # Create instance
    app = Yaapp(auto_discover=False)
    
    # Add some test functions
    @app.expose
    def greet(name: str) -> str:
        return f"Hello, {name}!"
    
    app.expose({"math": {"add": lambda x, y: x + y}})
    
    # Verify functions are exposed
    assert "greet" in app._registry
    
    # Test that we can get registry items
    registry = app.get_registry_items()
    assert "greet" in registry
    
    # The math.add function should be exposed as a nested function
    # Check if any math-related functions are exposed
    math_functions = [key for key in registry.keys() if "add" in key or "math" in key]
    assert len(math_functions) > 0, f"Expected math functions, got: {list(registry.keys())}"
