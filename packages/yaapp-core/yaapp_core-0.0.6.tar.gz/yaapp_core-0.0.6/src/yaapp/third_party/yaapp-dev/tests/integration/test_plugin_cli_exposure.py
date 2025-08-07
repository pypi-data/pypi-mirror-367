#!/usr/bin/env python3
"""
Test plugin CLI exposure - ensuring plugin methods appear as root-level commands.

This test verifies that plugin discovery exposes plugin methods as individual
root-level commands, matching the behavior of task-manager and data-analyzer examples.
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
    
    def assert_not_in(self, item, container, message):
        self.assert_true(item not in container, message)
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\\n=== PLUGIN CLI EXPOSURE TEST SUMMARY ===")
        print(f"Total: {total}, Passed: {self.passed}, Failed: {self.failed}")
        if self.errors:
            print("\\nFAILED TESTS:")
            for error in self.errors:
                print(f"  {error}")
        return self.failed == 0


def create_test_plugin_app(plugin_config, app_content=None):
    """Create a temporary plugin app for testing."""
    temp_dir = tempfile.mkdtemp()
    
    # Create yaapp.json config
    config_file = Path(temp_dir) / "yaapp.json"
    with open(config_file, 'w') as f:
        json.dump(plugin_config, f, indent=2)
    
    # Create app.py
    if app_content is None:
        app_content = '''#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp import yaapp

if __name__ == "__main__":
    yaapp.run()
'''
    
    app_file = Path(temp_dir) / "app.py"
    with open(app_file, 'w') as f:
        f.write(app_content)
    
    return temp_dir


def run_app_command(app_dir, args=None):
    """Run the app with given arguments and return output."""
    if args is None:
        args = ["--help"]
    
    cmd = [sys.executable, "app.py"] + args
    
    try:
        result = subprocess.run(
            cmd,
            cwd=app_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"


def test_storage_plugin_cli_exposure(results):
    """Test that storage plugin methods appear as root-level commands."""
    print("\\n=== Testing Storage Plugin CLI Exposure ===")
    
    # Create storage plugin config
    config = {
        "app": {"name": "storage-test"},
        "storage": {
            "backend": "memory",
            "storage_dir": "./data"
        }
    }
    
    app_dir = create_test_plugin_app(config)
    
    try:
        # Run app --help and check output
        returncode, stdout, stderr = run_app_command(app_dir, ["--help"])
        
        # Should show storage plugin methods as root commands
        expected_commands = ["get", "set", "delete", "exists", "keys", "clear"]
        
        for cmd in expected_commands:
            results.assert_in(cmd, stdout, f"Storage command '{cmd}' appears in help")
        
        # Should not show 'storage' as a grouped command
        results.assert_not_in("storage\\n", stdout, "Storage plugin not shown as grouped command")
        
        # Test individual command help
        returncode, stdout, stderr = run_app_command(app_dir, ["set", "--help"])
        results.assert_in("--key", stdout, "Storage 'set' command shows key parameter")
        results.assert_in("--value", stdout, "Storage 'set' command shows value parameter")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(app_dir, ignore_errors=True)


def test_issues_plugin_cli_exposure(results):
    """Test that issues plugin methods appear as root-level commands."""
    print("\\n=== Testing Issues Plugin CLI Exposure ===")
    
    # Create issues plugin config
    config = {
        "app": {"name": "issues-test"},
        "issues": {
            "default_priority": "medium"
        },
        "storage": {
            "backend": "memory"
        }
    }
    
    app_dir = create_test_plugin_app(config)
    
    try:
        # Run app --help and check output
        returncode, stdout, stderr = run_app_command(app_dir, ["--help"])
        
        # Should show issues plugin methods as root commands
        expected_commands = ["create", "get", "update", "delete", "assign", "close"]
        
        for cmd in expected_commands:
            results.assert_in(cmd, stdout, f"Issues command '{cmd}' appears in help")
        
        # Should not show 'issues' as a grouped command
        results.assert_not_in("issues\\n", stdout, "Issues plugin not shown as grouped command")
        
        # Test individual command help
        returncode, stdout, stderr = run_app_command(app_dir, ["create", "--help"])
        results.assert_in("--title", stdout, "Issues 'create' command shows title parameter")
        results.assert_in("--description", stdout, "Issues 'create' command shows description parameter")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(app_dir, ignore_errors=True)


def test_multiple_plugins_cli_exposure(results):
    """Test that multiple plugins expose their methods correctly."""
    print("\\n=== Testing Multiple Plugins CLI Exposure ===")
    
    # Create config with multiple plugins
    config = {
        "app": {"name": "multi-plugin-test"},
        "storage": {
            "backend": "memory"
        },
        "issues": {
            "default_priority": "medium"
        }
    }
    
    app_dir = create_test_plugin_app(config)
    
    try:
        # Run app --help and check output
        returncode, stdout, stderr = run_app_command(app_dir, ["--help"])
        
        # Should show methods from both plugins
        storage_commands = ["get", "set", "delete", "exists", "keys", "clear"]
        issues_commands = ["create", "update", "assign", "close"]
        
        for cmd in storage_commands:
            results.assert_in(cmd, stdout, f"Storage command '{cmd}' appears with multiple plugins")
        
        for cmd in issues_commands:
            results.assert_in(cmd, stdout, f"Issues command '{cmd}' appears with multiple plugins")
        
        # Should still have built-in commands
        builtin_commands = ["list", "run", "server", "tui"]
        for cmd in builtin_commands:
            results.assert_in(cmd, stdout, f"Built-in command '{cmd}' still present")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(app_dir, ignore_errors=True)


def test_plugin_command_execution(results):
    """Test that plugin commands can actually be executed."""
    print("\\n=== Testing Plugin Command Execution ===")
    
    # Create storage plugin config
    config = {
        "app": {"name": "execution-test"},
        "storage": {
            "backend": "memory"
        }
    }
    
    app_dir = create_test_plugin_app(config)
    
    try:
        # Test storage set command
        returncode, stdout, stderr = run_app_command(app_dir, ["set", "--key=test", "--value=hello"])
        results.assert_true(returncode == 0, "Storage 'set' command executes successfully")
        
        # Test storage get command
        returncode, stdout, stderr = run_app_command(app_dir, ["get", "--key=test"])
        results.assert_true(returncode == 0, "Storage 'get' command executes successfully")
        
        # Test storage exists command
        returncode, stdout, stderr = run_app_command(app_dir, ["exists", "--key=test"])
        results.assert_true(returncode == 0, "Storage 'exists' command executes successfully")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(app_dir, ignore_errors=True)


def test_comparison_with_task_manager(results):
    """Test that plugin exposure matches task-manager pattern."""
    print("\n=== Testing Comparison with Task Manager Pattern ===")
    
    # Test plugin exposure follows expected pattern
    config = {
        "app": {"name": "pattern-test"},
        "storage": {
            "backend": "memory"
        }
    }
    
    app_dir = create_test_plugin_app(config)
    
    try:
        returncode, plugin_stdout, plugin_stderr = run_app_command(app_dir, ["--help"])
        
        # Extract commands from plugin output
        plugin_commands = []
        in_commands_section = False
        for line in plugin_stdout.split('\n'):
            if line.strip() == "Commands:":
                in_commands_section = True
                continue
            elif in_commands_section and line.strip() and not line.startswith('  '):
                break
            elif in_commands_section and line.strip().startswith('  '):
                cmd = line.strip().split()[0]
                if cmd not in ["list", "run", "server", "tui"]:  # Skip built-ins
                    plugin_commands.append(cmd)
        
        results.assert_true(len(plugin_commands) > 0, "Plugin app exposes individual commands")
        
        # Check that plugin commands appear at root level (not grouped)
        for cmd in plugin_commands:
            results.assert_true(len(cmd.split('.')) == 1, f"Plugin command '{cmd}' is at root level (not nested)")
        
        # Check that expected storage commands are present
        expected_storage_commands = ["get", "set", "delete", "exists"]
        for cmd in expected_storage_commands:
            results.assert_in(cmd, plugin_commands, f"Expected storage command '{cmd}' is present")
    
    finally:
        import shutil
        shutil.rmtree(app_dir, ignore_errors=True)


def test_existing_plugin_examples(results):
    """Test the actual plugin examples in the repository."""
    print("\\n=== Testing Existing Plugin Examples ===")
    
    examples_dir = Path(__file__).parent.parent.parent / "examples" / "plugins"
    
    # Test issues plugin example
    issues_dir = examples_dir / "issues"
    if issues_dir.exists():
        try:
            returncode, stdout, stderr = run_app_command(str(issues_dir), ["--help"])
            
            # Should show individual issue commands
            expected_commands = ["create", "get", "update", "delete"]
            for cmd in expected_commands:
                results.assert_in(cmd, stdout, f"Issues example shows '{cmd}' command")
            
            # Should not show 'issues' as grouped command
            results.assert_not_in("issues\\n", stdout, "Issues example doesn't show grouped 'issues' command")
            
        except Exception as e:
            results.assert_true(False, f"Issues example test failed: {e}")
    
    # Test storage plugin example
    storage_dir = examples_dir / "storage"
    if storage_dir.exists():
        try:
            returncode, stdout, stderr = run_app_command(str(storage_dir), ["--help"])
            
            # Should show individual storage commands
            expected_commands = ["get", "set", "delete", "exists"]
            for cmd in expected_commands:
                results.assert_in(cmd, stdout, f"Storage example shows '{cmd}' command")
            
            # Should not show 'storage' as grouped command
            results.assert_not_in("storage\\n", stdout, "Storage example doesn't show grouped 'storage' command")
            
        except Exception as e:
            results.assert_true(False, f"Storage example test failed: {e}")


def main():
    """Run all plugin CLI exposure tests."""
    print("🔧 Plugin CLI Exposure Tests")
    print("Testing that plugin discovery exposes methods as root-level commands")
    
    results = TestResults()
    
    # Run all test suites
    test_storage_plugin_cli_exposure(results)
    test_issues_plugin_cli_exposure(results)
    test_multiple_plugins_cli_exposure(results)
    test_plugin_command_execution(results)
    test_comparison_with_task_manager(results)
    test_existing_plugin_examples(results)
    
    # Show summary
    success = results.summary()
    
    if success:
        print("\\n🎉 ALL PLUGIN CLI EXPOSURE TESTS PASSED!")
        print("Plugin discovery correctly exposes methods as root-level commands.")
        print("Plugin examples now match task-manager and data-analyzer patterns.")
    else:
        print("\\n💥 PLUGIN CLI EXPOSURE TESTS FAILED!")
        print("Issues detected in plugin CLI exposure system.")
        sys.exit(1)


if __name__ == "__main__":
    main()