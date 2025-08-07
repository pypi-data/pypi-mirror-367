#!/usr/bin/env python3
"""
Demonstration of yapp's object reflection capabilities
"""

import os
import sys

# Add src to path so we can import yaapp
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from yaapp import Yaapp

# Create the demo application
app = Yaapp()

print("=== yapp Object Reflection Demo ===\n")


# 1. Simple functions
@app.expose
def greet(name: str = "World", formal: bool = False) -> str:
    """Greet someone with optional formality."""
    greeting = "Good day" if formal else "Hello"
    return f"{greeting}, {name}!"


@app.expose
def calculate_age(birth_year: int, current_year: int = 2024) -> int:
    """Calculate age from birth year."""
    return current_year - birth_year


print("✓ Added simple functions: greet, calculate_age")


# 2. Class with methods
@app.expose
class MathOperations:
    """Mathematical operations class."""

    def add(self, x: float = 0.0, y: float = 0.0) -> float:
        """Add two numbers."""
        return x + y

    def multiply(self, x: float = 1.0, y: float = 1.0) -> float:
        """Multiply two numbers."""
        return x * y

    def power(self, base: float = 2.0, exponent: float = 2.0) -> float:
        """Raise base to the power of exponent."""
        return base**exponent


print("✓ Added MathOperations class with methods: add, multiply, power")

# 3. Nested function hierarchies
app.expose(
    {
        "string_utils": {
            "upper": lambda text: text.upper(),
            "lower": lambda text: text.lower(),
            "reverse": lambda text: text[::-1],
            "word_count": lambda text: len(text.split()),
        },
        "file_utils": {
            "read_lines": lambda filename: f"Would read lines from {filename}",
            "write_text": lambda filename, content: f"Would write '{content}' to {filename}",
        },
        "data": {
            "analytics": {
                "mean": lambda values: sum(values) / len(values) if values else 0,
                "max_val": lambda values: max(values) if values else 0,
            }
        },
    }
)

print("✓ Added nested function hierarchies:")
print("  - string_utils.*")
print("  - file_utils.*")
print("  - data.analytics.*")

# Show the registry structure
print(f"\n=== Registry Contents ({len(app._registry)} items) ===")
for name, obj in sorted(app._registry.items()):
    obj_type = type(obj).__name__
    if hasattr(obj, "__name__"):
        obj_name = obj.__name__
    else:
        obj_name = str(obj)[:50] + "..." if len(str(obj)) > 50 else str(obj)

    print(f"  {name:<25} | {obj_type:<10} | {obj_name}")

print("\n=== Expected Click Command Structure ===")
print("When using click backend, this would create:")
print()
print("Root commands:")
print("  ├── help                    # Show help")
print("  ├── list                    # List functions")
print("  ├── server                  # Start web server")
print("  ├── tui                     # Start TUI")
print("  ├── run                     # Execute functions")
print("  ├── greet                   # Direct function access")
print("  │   ├── --name              # String parameter")
print("  │   └── --formal            # Boolean flag")
print("  ├── calculate-age           # Direct function access")
print("  │   ├── --birth-year        # Integer parameter")
print("  │   └── --current-year      # Integer parameter")
print("  ├── MathOperations          # Class as command group")
print("  │   ├── add                 # Method as subcommand")
print("  │   │   ├── --x             # Float parameter")
print("  │   │   └── --y             # Float parameter")
print("  │   ├── multiply            # Method as subcommand")
print("  │   │   ├── --x             # Float parameter")
print("  │   │   └── --y             # Float parameter")
print("  │   └── power               # Method as subcommand")
print("  │       ├── --base          # Float parameter")
print("  │       └── --exponent      # Float parameter")
print("  ├── string-utils            # Nested group")
print("  │   ├── upper               # Function")
print("  │   ├── lower               # Function")
print("  │   ├── reverse             # Function")
print("  │   └── word-count          # Function")
print("  ├── file-utils              # Nested group")
print("  │   ├── read-lines          # Function")
print("  │   └── write-text          # Function")
print("  └── data                    # Nested group")
print("      └── analytics           # Sub-nested group")
print("          ├── mean            # Function")
print("          └── max-val         # Function")

print("\n=== TUI Backend Examples ===")
print("1. Typer TUI (simple, no dependencies):")
print("   yapp> greet --name=Alice --formal")
print("   Result: Good day, Alice!")
print()
print("2. Rich TUI (with colors and tables):")
print("   Shows functions in a nice table format")
print("   Supports JSON output formatting")
print()
print("3. Prompt Toolkit TUI:")
print("   Auto-completion for function names")
print("   History and advanced editing")
print()
print("4. Click TUI:")
print("   Full click CLI with --help for each command")
print("   Hierarchical command structure")
print("   Example: MathOperations add --help")

print("\n=== Testing Function Calls ===")

# Test some function calls
test_cases = [
    ("greet", ["--name=Alice"]),
    ("greet", ["--name=Bob", "--formal"]),
    ("calculate_age", ["--birth-year=1990"]),
]

for func_name, args in test_cases:
    try:
        if func_name in app._registry:
            result = app._call_function_with_args(app._registry[func_name], args)
            print(f"✓ {func_name} {' '.join(args)} -> {result}")
        else:
            print(f"✗ {func_name} not found")
    except Exception as e:
        print(f"✗ {func_name} error: {e}")

print("\n🎉 Demo completed!")
print("To test interactively:")
print("  python demo_reflection.py  # This demo")
print("  # Or with examples:")
print("  cd examples/data-analyzer && python app.py tui --backend typer")
print("  cd examples/file-processor && python app.py list")
