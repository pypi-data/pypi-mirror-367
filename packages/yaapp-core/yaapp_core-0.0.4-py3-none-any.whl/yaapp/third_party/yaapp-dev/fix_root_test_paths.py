#!/usr/bin/env python3
"""Fix test paths for root directory structure."""

import os
import re
from pathlib import Path

def fix_test_path(file_path):
    """Fix the sys.path.insert line for root directory tests."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern for the old path (designed for claude subdirectory)
    old_pattern = r"sys\.path\.insert\(0, os\.path\.join\(os\.path\.dirname\(os\.path\.dirname\(os\.path\.dirname\(os\.path\.dirname\(__file__\)\)\)\), 'src'\)\)"
    
    # New pattern for root directory
    new_replacement = "sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))"
    
    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_replacement, content)
        
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Fixed: {file_path}")
        return True
    
    return False

def main():
    """Fix all test files in the tests directory."""
    tests_dir = Path("tests")
    
    fixed_count = 0
    for test_file in tests_dir.rglob("*.py"):
        if test_file.name != "__init__.py":
            if fix_test_path(test_file):
                fixed_count += 1
    
    print(f"\nFixed {fixed_count} test files for root directory structure.")

if __name__ == "__main__":
    main()