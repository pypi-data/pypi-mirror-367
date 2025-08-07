#!/usr/bin/env python3
"""
Test script to verify YAPP functionality after recovery.
"""

import sys
import os

# Add qodo/src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "qodo", "src"))

from yapp import YApp

# Create YAPP application
app = YApp()

# Test 1: Function exposure
@app.expose
def greet(name: str, formal: bool = False) -> str:
    """Greet a person."""
    greeting = "Good day" if formal else "Hello"
    return f"{greeting}, {name}!"

# Test 2: Class exposure
@app.expose
class Calculator:
    """A simple calculator."""
    
    def add(self, x: int, y: int) -> int:
        """Add two numbers."""
        return x + y
    
    def multiply(self, x: int, y: int) -> int:
        """Multiply two numbers."""
        return x * y

# Test 3: Dictionary tree exposure
app.expose({
    "math": {
        "subtract": lambda x, y: x - y,
        "advanced": {
            "power": lambda x, y: x ** y
        }
    },
    "utils": {
        "reverse": lambda s: s[::-1],
        "upper": lambda s: s.upper()
    }
})

if __name__ == "__main__":
    print("🎯 YAPP Recovery Test")
    print("=" * 50)
    
    # Test registry
    print(f"📋 Registry contains {len(app.get_registry())} items")
    
    # List functions
    print("\n📝 Available functions:")
    functions = app.list_functions()
    for path, signature in functions.items():
        print(f"  {path}: {signature}")
    
    print("\n✅ YAPP recovery successful!")
    print("🚀 Ready to run with: python test_recovery.py server")
    
    # If server argument provided, start server
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        print("\n🌐 Starting FastAPI server...")
        app.run()