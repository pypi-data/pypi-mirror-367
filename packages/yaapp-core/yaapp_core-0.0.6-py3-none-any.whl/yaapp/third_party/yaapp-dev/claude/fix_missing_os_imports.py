#!/usr/bin/env python3
"""Fix missing 'import os' statements in test files."""

import os
import re
from pathlib import Path

def fix_missing_os_import(file_path):
    """Add 'import os' if it's missing but os.path is used."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if file uses os.path but doesn't import os
    uses_os_path = 'os.path' in content or 'os.path.join' in content
    has_os_import = re.search(r'^import os$', content, re.MULTILINE)
    
    if uses_os_path and not has_os_import:
        # Find the best place to add the import (after other imports)
        lines = content.split('\n')
        insert_index = 0
        
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                insert_index = i + 1
            elif line.startswith('sys.path.insert'):
                # Insert os import right before sys.path.insert line
                insert_index = i
                break
        
        lines.insert(insert_index, 'import os')
        content = '\n'.join(lines)
        
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Added 'import os' to: {file_path}")
        return True
    
    return False

def main():
    """Fix all test files in the tests directory."""
    tests_dir = Path("tests")
    
    fixed_count = 0
    for test_file in tests_dir.rglob("*.py"):
        if fix_missing_os_import(test_file):
            fixed_count += 1
    
    print(f"\nAdded 'import os' to {fixed_count} test files.")

if __name__ == "__main__":
    main()