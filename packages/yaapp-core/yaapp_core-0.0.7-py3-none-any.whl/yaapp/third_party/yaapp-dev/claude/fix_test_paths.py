#!/usr/bin/env python3
"""Fix import paths in all test files after reorganization."""

import os
import re
from pathlib import Path

def fix_test_file(file_path):
    """Fix the sys.path.insert line in a test file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern for the incorrect sys.path.insert line
    patterns = [
        r"import os; sys\.path\.insert\(0, os\.path\.join\(os\.path\.dirname\(os\.path\.dirname\(__file__\)\), 'src'\)\)",
        r"import os; sys\.path\.insert\(0, os\.path\.join\(os\.path\.dirname\(os\.path\.dirname\(__file__\)\), \"src\"\)\)",
        r"sys\.path\.insert\(0, os\.path\.join\(os\.path\.dirname\(os\.path\.dirname\(__file__\)\), 'src'\)\)",
        r"sys\.path\.insert\(0, os\.path\.join\(os\.path\.dirname\(os\.path\.dirname\(__file__\)\), \"src\"\)\)"
    ]
    
    # Correct replacement for subdirectory tests
    replacement = "sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'src'))"
    
    modified = False
    for pattern in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    # Also fix the conftest.py file path (it's one level up)
    if file_path.name == 'conftest.py':
        conftest_replacement = "sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))"
        content = re.sub(
            r"sys\.path\.insert\(0, os\.path\.join\(os\.path\.dirname\(__file__\), 'src'\)\)",
            conftest_replacement, 
            content
        )
        modified = True
    
    if modified:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Fixed: {file_path}")
    
    return modified

def main():
    """Fix all test files in the tests directory."""
    tests_dir = Path("tests")
    
    fixed_count = 0
    for test_file in tests_dir.rglob("*.py"):
        if fix_test_file(test_file):
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} test files.")

if __name__ == "__main__":
    main()