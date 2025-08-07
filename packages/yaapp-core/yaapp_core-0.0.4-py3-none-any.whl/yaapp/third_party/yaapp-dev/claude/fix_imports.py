#!/usr/bin/env python3
"""
Fix import patterns in all test files - remove sys.path manipulation.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path: Path, relative_src_path: str):
    """Fix imports in a single test file."""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match sys.path.insert lines
    sys_path_pattern = r'sys\.path\.insert\(0,\s*[\'"]src[\'"]\)'
    
    # Check if file has sys.path manipulation
    if not re.search(sys_path_pattern, content):
        return False, "No sys.path found"
    
    # Replace sys.path.insert with proper path
    new_src_path = relative_src_path
    
    # Remove the sys.path.insert line and add proper path
    lines = content.split('\n')
    new_lines = []
    found_sys_path = False
    added_new_path = False
    
    for line in lines:
        if re.search(sys_path_pattern, line):
            # Replace with proper path addition
            if not added_new_path:
                new_lines.append(f'sys.path.insert(0, "{new_src_path}")')
                added_new_path = True
                found_sys_path = True
            # Skip this line (don't add duplicate)
        else:
            new_lines.append(line)
    
    if found_sys_path:
        new_content = '\n'.join(new_lines)
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        return True, "Fixed sys.path"
    
    return False, "No changes needed"

def fix_all_imports():
    """Fix imports in all test files."""
    
    print("🔧 Fixing import patterns in all test files...")
    print("=" * 50)
    
    # Define paths relative to different test directories
    paths = {
        'tests/unit': '../../src',
        'tests/integration': '../../src', 
        'tests/interface': '../../src',
        'tests/performance': '../../src',
        '.': 'src'  # Root directory files
    }
    
    fixed_count = 0
    total_count = 0
    
    for test_dir, relative_path in paths.items():
        test_path = Path(test_dir)
        
        if not test_path.exists():
            continue
            
        print(f"\n📁 Processing {test_dir}:")
        
        # Find all test files in this directory
        test_files = list(test_path.glob('test_*.py'))
        
        for test_file in test_files:
            total_count += 1
            
            try:
                fixed, message = fix_imports_in_file(test_file, relative_path)
                
                if fixed:
                    print(f"  ✅ {test_file.name} - {message}")
                    fixed_count += 1
                else:
                    print(f"  ⚪ {test_file.name} - {message}")
                    
            except Exception as e:
                print(f"  ❌ {test_file.name} - Error: {e}")
    
    print(f"\n📊 Import Fix Summary:")
    print(f"  ✅ Fixed: {fixed_count} files")
    print(f"  📂 Total processed: {total_count} files")
    
    return fixed_count, total_count

def test_fixed_imports():
    """Test that fixed imports work."""
    
    print(f"\n🧪 Testing fixed imports...")
    
    # Test a few key files
    test_files = [
        'tests/unit/test_argument_parsing_fix.py',
        'tests/integration/test_comprehensive.py',
    ]
    
    success_count = 0
    
    for test_file in test_files:
        if not Path(test_file).exists():
            continue
            
        try:
            # Try to import the test file
            import subprocess
            result = subprocess.run(['python', '-c', f'exec(open("{test_file}").read())'], 
                                  capture_output=True, text=True, cwd=Path(test_file).parent)
            
            if result.returncode == 0:
                print(f"  ✅ {test_file} - imports work")
                success_count += 1
            else:
                print(f"  ❌ {test_file} - import error: {result.stderr.split(chr(10))[0]}")
                
        except Exception as e:
            print(f"  ❌ {test_file} - test error: {e}")
    
    return success_count

if __name__ == "__main__":
    fixed, total = fix_all_imports()
    
    if fixed > 0:
        print(f"\n🎉 Import fixes completed! Fixed {fixed}/{total} files")
        test_fixed_imports()
    else:
        print(f"\n⚪ No import fixes needed")