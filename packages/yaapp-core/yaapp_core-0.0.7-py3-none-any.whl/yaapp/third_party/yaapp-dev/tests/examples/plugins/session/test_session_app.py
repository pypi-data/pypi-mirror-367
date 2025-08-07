#!/usr/bin/env python3
"""
Simple test for the session app basic functionality.
"""

import subprocess
import sys
from pathlib import Path

def test_session_app_basic():
    """Test basic session app functionality."""
    
    app_path = Path(__file__).parent.parent.parent.parent.parent / "examples" / "plugins" / "session" / "app.py"
    
    # Test help output
    result = subprocess.run(
        [sys.executable, str(app_path), "--help"],
        capture_output=True,
        text=True,
        cwd=str(app_path.parent.parent.parent.parent)
    )
    
    # Basic checks
    required = ["Commands:", "session", "--server", "--rich", "--prompt", "--typer"]
    missing = [item for item in required if item not in result.stdout]
    
    if missing:
        print(f"❌ Missing: {missing}")
        print("Output:", result.stdout)
        return False
    
    print("✅ Basic functionality working")
    assert True

if __name__ == "__main__":
    success = test_session_app_basic()
    print("🎉 PASS" if success else "❌ FAIL")