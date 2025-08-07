#!/usr/bin/env python3
"""
Migrate test files to proper directory structure.
"""

import os
import shutil
from pathlib import Path

# Define test categories and their destination directories
TEST_CATEGORIES = {
    # Unit tests for individual components
    'unit': [
        'test_stateless_exposers.py',
        'test_argument_parsing_fix.py', 
        'test_class_execution_caching.py',
        'test_async_exposers.py',
        'test_async_compat.py',
        'test_config.py',
        'test_basic.py',
        'test_edge_cases.py',
    ],
    
    # Integration tests for system components
    'integration': [
        'test_comprehensive.py',
        'test_discovery_optimization.py',
        'test_class_instantiation_discovery_fix.py',
        'test_integration.py',
        'test_bug_fixes.py',
        'test_rpc_integration.py',
        'test_appproxy.py',
        'test_async_integration.py',
        'test_async_proxy.py',
        'test_reflection_system_fix.py',
        'test_registry_fix.py',
        'test_runner_code_duplication_fix.py',
        'test_client.py',
        'test_server_mode.py',
        'test_web_mode.py',
        'test_click_reflection.py',
        'test_async_core.py',
        'test_data_analyzer.py',
        'test_new_fixes.py',
    ],
    
    # TUI and interface tests
    'interface': [
        'test_contextual_tui.py',
        'test_simple_tui.py', 
        'test_tui.py',
    ],
    
    # Performance tests
    'performance': [
        'test_discovery_optimization.py',  # Also performance
    ],
    
    # Keep in root (special cases)
    'root': [
        'test_run.py',  # Main runner test
        'tests/test_yapp.py',  # Already in tests/
    ]
}

def migrate_tests():
    """Migrate test files to proper directories."""
    
    print("🔄 Migrating test files to proper structure...")
    print("=" * 50)
    
    # Ensure test directories exist
    test_dirs = ['tests/unit', 'tests/integration', 'tests/interface', 'tests/performance']
    for test_dir in test_dirs:
        Path(test_dir).mkdir(parents=True, exist_ok=True)
        # Create __init__.py files
        init_file = Path(test_dir) / '__init__.py'
        if not init_file.exists():
            init_file.write_text('"""Test module."""\n')
    
    moved_count = 0
    skipped_count = 0
    
    # Process each category
    for category, files in TEST_CATEGORIES.items():
        if category == 'root':
            continue
            
        print(f"\n📁 Moving {category} tests:")
        
        for test_file in files:
            source = Path(test_file)
            
            if not source.exists():
                print(f"  ⚠️  {test_file} - not found")
                skipped_count += 1
                continue
            
            # Determine destination
            if category == 'performance' and test_file in TEST_CATEGORIES.get('integration', []):
                # Some files are both integration and performance - put in integration
                if test_file in TEST_CATEGORIES['integration']:
                    dest_dir = 'tests/integration'
                else:
                    dest_dir = f'tests/{category}'
            else:
                dest_dir = f'tests/{category}'
            
            dest = Path(dest_dir) / test_file
            
            try:
                shutil.move(str(source), str(dest))
                print(f"  ✅ {test_file} → {dest_dir}/")
                moved_count += 1
            except Exception as e:
                print(f"  ❌ {test_file} - error: {e}")
                skipped_count += 1
    
    print(f"\n📊 Migration Summary:")
    print(f"  ✅ Moved: {moved_count} files")
    print(f"  ⚠️  Skipped: {skipped_count} files")
    
    # List remaining test files in root
    remaining = list(Path('.').glob('test_*.py'))
    if remaining:
        print(f"\n📂 Remaining in root ({len(remaining)} files):")
        for f in remaining:
            print(f"  - {f.name}")
    
    print(f"\n🎉 Test migration completed!")
    return moved_count, skipped_count

if __name__ == "__main__":
    migrate_tests()