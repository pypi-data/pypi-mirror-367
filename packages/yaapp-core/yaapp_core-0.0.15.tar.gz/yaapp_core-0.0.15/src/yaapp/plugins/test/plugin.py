"""
Test plugin with streaming capabilities.
Contains both class methods and free functions for testing streaming endpoints.
"""

import random
import string
from typing import Generator


class Test:
    """Test class with various methods including streaming."""
    
    def get_info(self) -> dict:
        """Get basic plugin information."""
        return {
            "plugin": "test",
            "version": "1.0.0",
            "description": "Test plugin for streaming endpoints"
        }
    
    def stream_data(self, count: int = 10) -> Generator[str, None, None]:
        """Stream a list of random strings."""
        if count > 50:
            count = 50  # Max 50 items
        
        for i in range(count):
            # Generate random string of 8 characters
            random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            yield f"test_stream_{i}_{random_str}"


# Free functions
def get_status() -> dict:
    """Get plugin status."""
    return {
        "status": "active",
        "timestamp": "2025-01-08",
        "plugin": "test"
    }


def stream_random_words(count: int = 5) -> Generator[str, None, None]:
    """Stream random words."""
    if count > 50:
        count = 50  # Max 50 items
        
    word_parts = ["test", "stream", "data", "random", "word", "plugin", "server", "endpoint"]
    
    for i in range(count):
        word = random.choice(word_parts) + "_" + str(i) + "_" + ''.join(random.choices(string.ascii_lowercase, k=4))
        yield word


def calculate(x: int, y: int, operation: str = "add") -> dict:
    """Perform calculation."""
    if operation == "add":
        result = x + y
    elif operation == "multiply":
        result = x * y
    elif operation == "subtract":
        result = x - y
    else:
        result = 0
        
    return {
        "operation": operation,
        "x": x,
        "y": y,
        "result": result
    }