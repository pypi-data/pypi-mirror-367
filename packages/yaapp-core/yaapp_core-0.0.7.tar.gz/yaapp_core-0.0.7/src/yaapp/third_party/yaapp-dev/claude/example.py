#!/usr/bin/env python3
"""
Example usage of yapp - demonstrating both decorator and method call approaches
"""

from src.yaapp import Yaapp

# Create yapp instance
app = Yaapp()


# Example 1: Using as decorator
@app.expose
def greet(name: str, formal: bool = False) -> str:
    """Greet a person."""
    greeting = "Good day" if formal else "Hello"
    return f"{greeting}, {name}!"


@app.expose
class Calculator:
    """A simple calculator class."""

    def add(self, x: int, y: int) -> int:
        """Add two numbers."""
        return x + y

    def multiply(self, x: int, y: int) -> int:
        """Multiply two numbers."""
        return x * y


# Example 2: Using as method call with dictionary tree
def subtract(x: int, y: int) -> int:
    """Subtract two numbers."""
    return x - y


def divide(x: int, y: int) -> float:
    """Divide two numbers."""
    if y == 0:
        raise ValueError("Cannot divide by zero")
    return x / y


# Expose additional functions as a tree
app.expose(
    {
        "math": {
            "basic": {"subtract": subtract, "divide": divide},
            "advanced": {"power": lambda x, y: x**y, "sqrt": lambda x: x**0.5},
        },
        "utils": {"reverse_string": lambda s: s[::-1], "upper": lambda s: s.upper()},
    }
)

if __name__ == "__main__":
    # Context-aware execution
    app.run()
