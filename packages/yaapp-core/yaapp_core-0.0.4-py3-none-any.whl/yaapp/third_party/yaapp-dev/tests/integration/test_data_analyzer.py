#!/usr/bin/env python3
"""
Test data-analyzer example works after registry fix.
"""

import sys
sys.path.insert(0, "../../src")

from yaapp import Yaapp

# Test basic app creation like in data-analyzer
app = Yaapp()

@app.expose
def analyze_data(file_path: str = "sample.csv") -> dict:
    """Simple data analysis function."""
    return {"message": f"Analyzed {file_path}", "rows": 100}

@app.expose
class DataProcessor:
    """Simple data processor class."""
    def process(self, data: str) -> str:
        return f"Processed: {data}"

def test_data_analyzer_pattern():
    """Test the data analyzer pattern works."""
    # Check registry has our items
    assert 'analyze_data' in app._registry
    assert 'DataProcessor' in app._registry
    
    print("✅ Data analyzer pattern test passed")
    print(f"Registry has: {list(app._registry.keys())}")

if __name__ == "__main__":
    test_data_analyzer_pattern()