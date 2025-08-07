#!/usr/bin/env python3
"""
Test configuration file discovery from different directories.

This test verifies that config files are found correctly when running
yaapp applications from different working directories.
"""

import sys
import os
import subprocess
import tempfile
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestResults_:
    """Track test results."""
    passed = 0
    failed = 0
    errors = []
    
    def assert_true(self, condition, message):
        if condition:
            self.passed += 1
            print(f"✅ {message}")
        else:
            self.failed += 1
            error = f"❌ {message}"
            print(error)
            self.errors.append(error)
    
    def assert_false(self, condition, message):
        self.assert_true(not condition, message)
    
    def assert_in(self, item, container, message):
        self.assert_true(item in container, message)
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\\n=== CONFIG FILE DISCOVERY TEST SUMMARY ===")
        print(f"Total: {total}, Passed: {self.passed}, Failed: {self.failed}")
        if self.errors:
            print("\\nFAILED TESTS:")
            for error in self.errors:
                print(f"  {error}")
        return self.failed == 0


def create_test_app_with_config(app_dir, config_data):
    """Create a test app with config file in specified directory."""
    app_dir = Path(app_dir)
    app_dir.mkdir(parents=True, exist_ok=True)
    
    # Create yaapp.json config
    config_file = app_dir / "yaapp.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    # Create app.py
    app_content = '''#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp import yaapp

if __name__ == "__main__":
    yaapp.run()
'''
    
    app_file = app_dir / "app.py"
    with open(app_file, 'w') as f:
        f.write(app_content)
    
    return app_dir, app_file, config_file


def run_app_from_directory(app_file, working_dir, args=None):
    """Run the app from a specific working directory."""
    if args is None:
        args = ["--help"]
    
    cmd = [sys.executable, str(app_file)] + args
    
    try:
        result = subprocess.run(
            cmd,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"


def test_config_discovery_from_script_directory(results):
    """Test config discovery when running from script directory."""
    print("\\n=== Testing Config Discovery from Script Directory ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test app with storage plugin config
        config = {
            "app": {"name": "test-app"},
            "storage": {"backend": "memory"}
        }
        
        app_dir, app_file, config_file = create_test_app_with_config(temp_dir, config)
        
        # Run from script directory
        returncode, stdout, stderr = run_app_from_directory(app_file, app_dir, ["--help"])
        
        # Should find config and load storage plugin
        results.assert_in("storage", stdout, "Storage plugin loaded when running from script directory")
        results.assert_in("get", stdout, "Storage commands available")
        results.assert_in("set", stdout, "Storage commands available")


def test_config_discovery_from_different_directory(results):
    """Test config discovery when running from different directory."""
    print("\\n=== Testing Config Discovery from Different Directory ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test app with issues plugin config
        config = {
            "app": {"name": "test-app"},
            "issues": {"default_priority": "medium"},
            "storage": {"backend": "memory"}
        }
        
        app_dir, app_file, config_file = create_test_app_with_config(temp_dir, config)
        
        # Run from root directory (different from script directory)
        returncode, stdout, stderr = run_app_from_directory(app_file, "/tmp", ["--help"])
        
        # Should still find config and load plugins
        results.assert_in("issues", stdout, "Issues plugin loaded when running from different directory")
        results.assert_in("storage", stdout, "Storage plugin loaded when running from different directory")
        results.assert_in("create", stdout, "Issues commands available")
        results.assert_in("get", stdout, "Storage commands available")


def test_current_directory_override(results):
    """Test that current directory config overrides script directory config."""
    print("\\n=== Testing Current Directory Override ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create script directory with one config
        script_config = {
            "app": {"name": "script-app"},
            "storage": {"backend": "memory"}
        }
        
        script_dir, app_file, script_config_file = create_test_app_with_config(
            Path(temp_dir) / "script", script_config
        )
        
        # Create working directory with different config
        working_dir = Path(temp_dir) / "working"
        working_dir.mkdir()
        
        current_config = {
            "app": {"name": "current-app"},
            "issues": {"default_priority": "high"}
        }
        
        current_config_file = working_dir / "yaapp.json"
        with open(current_config_file, 'w') as f:
            json.dump(current_config, f, indent=2)
        
        # Run from working directory
        returncode, stdout, stderr = run_app_from_directory(app_file, working_dir, ["--help"])
        
        # Should use current directory config (issues, not storage)
        results.assert_in("issues", stdout, "Current directory config takes precedence")
        results.assert_in("create", stdout, "Issues commands from current directory config")
        
        # Should NOT have storage commands from script directory
        results.assert_true("storage" not in stdout or stdout.count("storage") == 0, 
                          "Script directory config overridden by current directory")


def test_no_config_file_graceful_handling(results):
    """Test graceful handling when no config file is found."""
    print("\\n=== Testing No Config File Graceful Handling ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create app without config file
        app_dir = Path(temp_dir) / "no-config"
        app_dir.mkdir()
        
        app_content = '''#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp import yaapp

if __name__ == "__main__":
    yaapp.run()
'''
        
        app_file = app_dir / "app.py"
        with open(app_file, 'w') as f:
            f.write(app_content)
        
        # Run from app directory
        returncode, stdout, stderr = run_app_from_directory(app_file, app_dir, ["--help"])
        
        # Should still work with built-in commands only
        results.assert_in("list", stdout, "Built-in commands available without config")
        results.assert_in("run", stdout, "Built-in commands available without config")
        results.assert_in("server", stdout, "Built-in commands available without config")
        
        # Should not have plugin commands
        results.assert_true("storage" not in stdout, "No plugin commands without config")
        results.assert_true("issues" not in stdout, "No plugin commands without config")


def test_config_search_paths_programmatically(results):
    """Test config search paths programmatically."""
    print("\\n=== Testing Config Search Paths Programmatically ===")
    
    try:
        from yaapp.core import YaappCore
        
        # Create core instance
        core = YaappCore()
        
        # Get search paths
        search_paths = core._get_config_search_paths()
        
        results.assert_true(len(search_paths) > 0, "At least one search path returned")
        
        # First path should be current working directory
        results.assert_true(search_paths[0] == Path.cwd(), "First search path is current working directory")
        
        # Should have unique paths
        unique_paths = list(set(search_paths))
        results.assert_true(len(unique_paths) == len(search_paths), "Search paths are unique")
        
        print(f"Search paths found: {[str(p) for p in search_paths]}")
        
    except Exception as e:
        results.assert_true(False, f"Config search paths test failed: {e}")


def test_existing_plugin_examples_from_root(results):
    """Test that existing plugin examples work from root directory."""
    print("\\n=== Testing Existing Plugin Examples from Root ===")
    
    # Test issues plugin example
    issues_app = Path(__file__).parent.parent.parent / "examples" / "plugins" / "issues" / "app.py"
    
    if issues_app.exists():
        try:
            returncode, stdout, stderr = run_app_from_directory(issues_app, "/tmp", ["--help"])
            
            results.assert_in("create", stdout, "Issues example works from root directory")
            results.assert_in("get", stdout, "Issues example works from root directory")
            results.assert_in("update", stdout, "Issues example works from root directory")
            
        except Exception as e:
            results.assert_true(False, f"Issues example test failed: {e}")
    
    # Test storage plugin example
    storage_app = Path(__file__).parent.parent.parent / "examples" / "plugins" / "storage" / "app.py"
    
    if storage_app.exists():
        try:
            returncode, stdout, stderr = run_app_from_directory(storage_app, "/tmp", ["--help"])
            
            results.assert_in("get", stdout, "Storage example works from root directory")
            results.assert_in("set", stdout, "Storage example works from root directory")
            results.assert_in("delete", stdout, "Storage example works from root directory")
            
        except Exception as e:
            results.assert_true(False, f"Storage example test failed: {e}")


def main():
    """Run all config file discovery tests."""
    print("🔧 Configuration File Discovery Tests")
    print("Testing config file discovery from different working directories")
    
    results = TestResults()
    
    # Run all test suites
    test_config_discovery_from_script_directory(results)
    test_config_discovery_from_different_directory(results)
    test_current_directory_override(results)
    test_no_config_file_graceful_handling(results)
    test_config_search_paths_programmatically(results)
    test_existing_plugin_examples_from_root(results)
    
    # Show summary
    success = results.summary()
    
    if success:
        print("\\n🎉 ALL CONFIG FILE DISCOVERY TESTS PASSED!")
        print("Configuration files are correctly discovered from multiple locations.")
        print("Plugin examples work from any directory.")
    else:
        print("\\n💥 CONFIG FILE DISCOVERY TESTS FAILED!")
        print("Issues detected in configuration file discovery system.")
        sys.exit(1)


if __name__ == "__main__":
    main()