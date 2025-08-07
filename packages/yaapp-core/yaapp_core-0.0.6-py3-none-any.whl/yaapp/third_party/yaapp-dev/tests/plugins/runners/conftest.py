"""
Shared test fixtures for runner tests.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from yaapp import Yaapp


@pytest.fixture
def test_app():
    """Create a test yaapp instance with sample functions."""
    app = Yaapp(auto_discover=False)
    
    # Add test functions
    @app.expose
    def add(x: int, y: int) -> int:
        """Add two numbers."""
        return x + y
    
    @app.expose
    def greet(name: str, formal: bool = False) -> str:
        """Greet someone."""
        return f"{'Good day' if formal else 'Hello'}, {name}!"
    
    @app.expose
    class Calculator:
        """Test calculator class."""
        
        def multiply(self, x: float, y: float) -> float:
            """Multiply two numbers."""
            return x * y
        
        def divide(self, x: float, y: float) -> float:
            """Divide two numbers."""
            if y == 0:
                raise ValueError("Cannot divide by zero")
            return x / y
    
    @app.expose("math.power")
    def power(base: float, exponent: float) -> float:
        """Calculate power."""
        return base ** exponent
    
    return app


@pytest.fixture
def runner_kwargs():
    """Default kwargs for runner tests."""
    return {
        'host': 'localhost',
        'port': 0,  # Use random port for tests
        'timeout': 2  # Short timeout for tests
    }