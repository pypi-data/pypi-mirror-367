#!/usr/bin/env python3
"""
Test CLI reflection for class instances (the fix for plugin discovery).

This test specifically covers the fix where class instances (from plugin discovery)
should be reflected as command groups with methods as subcommands.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False


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
    
    def assert_not_none(self, obj, message):
        self.assert_true(obj is not None, message)
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\\n=== CLI INSTANCE REFLECTION TEST SUMMARY ===")
        print(f"Total: {total}, Passed: {self.passed}, Failed: {self.failed}")
        if self.errors:
            print("\\nFAILED TESTS:")
            for error in self.errors:
                print(f"  {error}")
        return self.failed == 0


def test_instance_reflection_basic(results):
    """Test basic instance reflection functionality."""
    print("\\n=== Testing Basic Instance Reflection ===")
    
    try:
        from yaapp import Yaapp
        
        # Create app
        app = Yaapp(auto_discover=False)
        
        # Create a test class instance
        class TestPlugin:
            def __init__(self, config=None):
                self.config = config or {}
                self.yaapp = None
            
            def create(self, title: str, description: str = "") -> dict:
                """Create something."""
                return {"title": title, "description": description}
            
            def get(self, item_id: int) -> dict:
                """Get something by ID."""
                return {"id": item_id, "found": True}
            
            def list(self, status: str = "active") -> list:
                """List items."""
                return [{"status": status, "count": 5}]
        
        # Create instance and expose it (like plugin discovery does)
        plugin_instance = TestPlugin({"test": True})
        plugin_instance.yaapp = app
        
        expose_result = app.expose(plugin_instance, name="test_plugin")
        results.assert_true(expose_result.is_ok(), "Plugin instance exposed successfully")
        
        # Check registry contains the instance
        registry_items = app.get_registry_items()
        results.assert_in("test_plugin", registry_items, "Plugin instance in registry")
        
        # Verify it's an instance, not a class
        plugin_obj = registry_items["test_plugin"]
        results.assert_true(hasattr(plugin_obj, '__class__'), "Registry contains instance")
        results.assert_false(callable(plugin_obj) and hasattr(plugin_obj, '__name__'), "Registry contains instance, not class")
        
        print(f"Registry object type: {type(plugin_obj)}")
        print(f"Registry object methods: {[m for m in dir(plugin_obj) if not m.startswith('_')]}")
        
    except Exception as e:
        results.assert_true(False, f"Basic instance reflection test failed: {e}")


def test_cli_reflection_for_instances(results):
    """Test that CLI reflection properly handles instances."""
    print("\\n=== Testing CLI Reflection for Instances ===")
    
    if not HAS_CLICK:
        print("⚠️  Click not available, skipping CLI reflection test")
        return
    
    try:
        from yaapp import Yaapp
        from yaapp.reflection import CommandReflector
        
        # Create app with instance
        app = Yaapp(auto_discover=False)
        
        class IssuesPlugin:
            def __init__(self, config=None):
                self.config = config or {}
                self.yaapp = None
            
            def create(self, title: str, description: str = "", priority: str = "medium") -> dict:
                """Create a new issue."""
                return {"title": title, "description": description, "priority": priority}
            
            def get(self, issue_id: int) -> dict:
                """Get issue by ID."""
                return {"id": issue_id, "title": f"Issue {issue_id}"}
            
            def update(self, issue_id: int, title: str = None, status: str = None) -> dict:
                """Update an issue."""
                updates = {}
                if title: updates["title"] = title
                if status: updates["status"] = status
                return {"id": issue_id, "updates": updates}
            
            def delete(self, issue_id: int) -> bool:
                """Delete an issue."""
                return True
        
        # Expose instance (like discovery system does)
        issues_instance = IssuesPlugin()
        issues_instance.yaapp = app
        app.expose(issues_instance, name="issues")
        
        # Test CLI reflection
        @click.group()
        def test_cli():
            """Test CLI group."""
            pass
        
        # Use CommandReflector to add reflected commands
        reflector = CommandReflector(app)
        reflector.add_reflected_commands(test_cli)
        
        # Check that the issues command group was created
        commands = getattr(test_cli, 'commands', {})
        results.assert_in("issues", commands, "Issues command group created")
        
        if "issues" in commands:
            issues_group = commands["issues"]
            
            # Check that it's a group (has commands)
            group_commands = getattr(issues_group, 'commands', {})
            results.assert_true(len(group_commands) > 0, "Issues group has subcommands")
            
            # Check specific methods are present
            expected_methods = ["create", "get", "update", "delete"]
            for method in expected_methods:
                results.assert_in(method, group_commands, f"Issues group has {method} command")
            
            print(f"Issues group commands: {list(group_commands.keys())}")
        
    except Exception as e:
        results.assert_true(False, f"CLI reflection for instances test failed: {e}")


def test_instance_vs_class_reflection(results):
    """Test that instances and classes are handled differently."""
    print("\\n=== Testing Instance vs Class Reflection ===")
    
    if not HAS_CLICK:
        print("⚠️  Click not available, skipping instance vs class test")
        return
    
    try:
        from yaapp import Yaapp
        from yaapp.reflection import CommandReflector
        
        app = Yaapp(auto_discover=False)
        
        class TestClass:
            def method1(self, x: int) -> int:
                return x * 2
            
            def method2(self, text: str) -> str:
                return text.upper()
        
        # Expose class (decorator pattern)
        app.expose(TestClass, name="test_class")
        
        # Expose instance (discovery pattern)
        test_instance = TestClass()
        app.expose(test_instance, name="test_instance")
        
        # Test reflection handles both
        @click.group()
        def test_cli():
            """Test CLI group."""
            pass
        
        reflector = CommandReflector(app)
        reflector.add_reflected_commands(test_cli)
        
        commands = getattr(test_cli, 'commands', {})
        
        # Both should create command groups
        results.assert_in("test_class", commands, "Class exposure creates command group")
        results.assert_in("test_instance", commands, "Instance exposure creates command group")
        
        # Both should have the same methods
        if "test_class" in commands and "test_instance" in commands:
            class_commands = getattr(commands["test_class"], 'commands', {})
            instance_commands = getattr(commands["test_instance"], 'commands', {})
            
            results.assert_in("method1", class_commands, "Class group has method1")
            results.assert_in("method2", class_commands, "Class group has method2")
            results.assert_in("method1", instance_commands, "Instance group has method1")
            results.assert_in("method2", instance_commands, "Instance group has method2")
        
    except Exception as e:
        results.assert_true(False, f"Instance vs class reflection test failed: {e}")


def test_plugin_discovery_integration(results):
    """Test the actual plugin discovery integration scenario."""
    print("\\n=== Testing Plugin Discovery Integration ===")
    
    if not HAS_CLICK:
        print("⚠️  Click not available, skipping plugin discovery integration test")
        return
    
    try:
        from yaapp import Yaapp
        
        # Simulate plugin discovery scenario
        app = Yaapp(auto_discover=False)
        
        # Create plugin classes (like the real plugins)
        class StoragePlugin:
            def __init__(self, config=None):
                self.config = config or {}
                self.yaapp = None
            
            def get(self, key: str, namespace: str = "default") -> str:
                """Get value by key."""
                return f"value_for_{key}_in_{namespace}"
            
            def set(self, key: str, value: str, namespace: str = "default") -> bool:
                """Set value by key."""
                return True
            
            def delete(self, key: str, namespace: str = "default") -> bool:
                """Delete value by key."""
                return True
        
        class IssuesPlugin:
            def __init__(self, config=None):
                self.config = config or {}
                self.yaapp = None
            
            def create(self, title: str, description: str, reporter: str) -> dict:
                """Create a new issue."""
                return {"id": "issue_123", "title": title, "description": description, "reporter": reporter}
            
            def get(self, issue_id: str) -> dict:
                """Get issue by ID."""
                return {"id": issue_id, "title": f"Issue {issue_id}"}
        
        # Simulate discovery system registering instances
        storage_instance = StoragePlugin({"backend": "memory"})
        storage_instance.yaapp = app
        app.expose(storage_instance, name="storage")
        
        issues_instance = IssuesPlugin({"default_priority": "medium"})
        issues_instance.yaapp = app
        app.expose(issues_instance, name="issues")
        
        # Test CLI creation (like the real CLI)
        from yaapp.reflection import ClickReflection
        reflection = ClickReflection(app)
        cli = reflection.create_reflective_cli()
        
        results.assert_not_none(cli, "CLI created successfully")
        
        if cli:
            commands = getattr(cli, 'commands', {})
            
            # Check plugin commands are present
            results.assert_in("storage", commands, "Storage plugin command group created")
            results.assert_in("issues", commands, "Issues plugin command group created")
            
            # Check built-in commands are still there
            results.assert_in("server", commands, "Built-in server command present")
            results.assert_in("list", commands, "Built-in list command present")
            
            # Check plugin subcommands
            if "storage" in commands:
                storage_commands = getattr(commands["storage"], 'commands', {})
                results.assert_in("get", storage_commands, "Storage has get command")
                results.assert_in("set", storage_commands, "Storage has set command")
                results.assert_in("delete", storage_commands, "Storage has delete command")
            
            if "issues" in commands:
                issues_commands = getattr(commands["issues"], 'commands', {})
                results.assert_in("create", issues_commands, "Issues has create command")
                results.assert_in("get", issues_commands, "Issues has get command")
        
    except Exception as e:
        results.assert_true(False, f"Plugin discovery integration test failed: {e}")


def main():
    """Run all CLI instance reflection tests."""
    print("🔧 CLI Instance Reflection Tests")
    print("Testing the fix for class instance reflection in CLI (plugin discovery scenario)")
    
    results = TestResults()
    
    # Run all test suites
    test_instance_reflection_basic(results)
    test_cli_reflection_for_instances(results)
    test_instance_vs_class_reflection(results)
    test_plugin_discovery_integration(results)
    
    # Show summary
    success = results.summary()
    
    if success:
        print("\\n🎉 ALL CLI INSTANCE REFLECTION TESTS PASSED!")
        print("The fix for class instance reflection is working correctly.")
        print("Plugin discovery now properly creates CLI command groups with method subcommands.")
    else:
        print("\\n💥 CLI INSTANCE REFLECTION TESTS FAILED!")
        print("Issues detected in class instance reflection fix.")
        sys.exit(1)


if __name__ == "__main__":
    main()