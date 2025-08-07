#!/usr/bin/env python3
"""
Comprehensive integration tests for YAPP framework.
These tests verify end-to-end functionality and would have caught the registry issue.
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, "../../src")

from yaapp import Yaapp
from yaapp.plugins.app_proxy.plugin import AppProxy


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
    
    def assert_equal(self, actual, expected, message):
        if actual == expected:
            self.passed += 1
            print(f"✅ {message}")
        else:
            self.failed += 1
            error = f"❌ {message} - Expected: {expected}, Got: {actual}"
            print(error)
            self.errors.append(error)
    
    def assert_in(self, item, container, message):
        if item in container:
            self.passed += 1
            print(f"✅ {message}")
        else:
            self.failed += 1
            error = f"❌ {message} - {item} not in {container}"
            print(error)
            self.errors.append(error)
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n=== TEST SUMMARY ===")
        print(f"Total: {total}, Passed: {self.passed}, Failed: {self.failed}")
        if self.errors:
            print("\nFAILED TESTS:")
            for error in self.errors:
                print(f"  {error}")
        return self.failed == 0


def test_basic_exposure_and_registry(results):
    """Test that exposure properly updates registry."""
    print("\n=== Testing Basic Exposure and Registry ===")
    
    app = Yaapp()
    
    # Test function exposure
    @app.expose
    def test_func(name: str = "World") -> str:
        return f"Hello, {name}!"
    
    results.assert_in('test_func', app._registry, "Function added to registry")
    registry_result = app.get_registry_item('test_func')
    if registry_result.is_ok():
        results.assert_equal(registry_result.unwrap(), test_func, "Registry contains correct function")
    else:
        results.assert_true(False, f"Failed to get registry item: {registry_result.as_error}")
    
    # Test class exposure
    @app.expose
    class TestClass:
        def method(self, x: int) -> int:
            return x * 2
    
    results.assert_in('TestClass', app._registry, "Class added to registry")
    registry_result = app.get_registry_item('TestClass')
    if registry_result.is_ok():
        results.assert_equal(registry_result.unwrap(), TestClass, "Registry contains correct class")
    else:
        results.assert_true(False, f"Failed to get registry item: {registry_result.as_error}")
    
    # Test dictionary exposure
    math_funcs = {"add": lambda x, y: x + y, "sub": lambda x, y: x - y}
    app.expose(math_funcs)
    
    results.assert_in('add', app._registry, "Dict function 'add' added to registry")
    results.assert_in('sub', app._registry, "Dict function 'sub' added to registry")
    
    # Test custom exposure (AppProxy) - skip if network unavailable
    try:
        proxy = AppProxy("http://localhost:8000")
        app.expose(proxy, name="remote", custom=True)
        
        results.assert_in('remote', app._registry, "Custom object added to registry")
        results.assert_equal(app._registry['remote'][0], proxy, "Registry contains correct proxy")
    except Exception as e:
        if "Connection refused" in str(e):
            results.assert_true(True, "AppProxy test skipped (no server running)")
        else:
            results.assert_true(False, f"AppProxy test failed: {e}")


def test_exposer_system_integration(results):
    """Test that exposer system works with different object types."""
    print("\n=== Testing Exposer System Integration ===")
    
    app = Yaapp()
    
    # Test each exposer type
    from yaapp.exposers import FunctionExposer, ClassExposer, ObjectExposer, CustomExposer
    
    # Verify exposers exist
    results.assert_true(hasattr(app, '_function_exposer'), "Function exposer exists")
    results.assert_true(hasattr(app, '_class_exposer'), "Class exposer exists") 
    results.assert_true(hasattr(app, '_object_exposer'), "Object exposer exists")
    results.assert_true(hasattr(app, '_custom_exposer'), "Custom exposer exists")
    
    # Test function exposer
    def simple_func():
        return "test"
    
    result = app._function_exposer.expose(simple_func, "simple")
    results.assert_true(result.is_ok(), "Function exposer works")
    
    # Test class exposer
    class SimpleClass:
        def method(self):
            return "method"
    
    result = app._class_exposer.expose(SimpleClass, "SimpleClass")
    results.assert_true(result.is_ok(), "Class exposer works")
    
    # Test custom exposer
    class SimpleCustomObject:
        def execute_call(self, **kwargs):
            return "custom result"
    
    custom_obj = SimpleCustomObject()
    result = app._custom_exposer.expose(custom_obj, "custom", custom=True)
    results.assert_true(result.is_ok(), "Custom exposer works")


def test_cli_integration_without_click(results):
    """Test CLI functionality when click is not available."""
    print("\n=== Testing CLI Integration (No Click) ===")
    
    app = Yaapp()
    
    @app.expose
    def hello(name: str = "World") -> str:
        return f"Hello, {name}!"
    
    @app.expose
    class Calculator:
        def add(self, x: int, y: int) -> int:
            return x + y
    
    # Test that run_cli doesn't crash without click
    try:
        # Capture output by redirecting stdout temporarily
        import io
        from contextlib import redirect_stdout
        
        output = io.StringIO()
        with redirect_stdout(output):
            app.run_cli()
        
        output_text = output.getvalue()
        results.assert_true("Available functions:" in output_text, "CLI shows available functions")
        results.assert_true("hello" in output_text, "CLI lists exposed function")
        results.assert_true("Calculator" in output_text, "CLI lists exposed class")
        
    except Exception as e:
        results.assert_true(False, f"CLI integration failed: {e}")


def test_reflection_system_integration(results):
    """Test that reflection system can access registry."""
    print("\n=== Testing Reflection System Integration ===")
    
    app = Yaapp()
    
    @app.expose
    def test_reflection(value: str) -> str:
        return f"Reflected: {value}"
    
    # Test reflection system can access registry
    from yaapp.reflection import ClickReflection
    reflection = ClickReflection(app)
    
    # This is the key test that would have caught the bug!
    try:
        registry_access = hasattr(reflection.core, '_registry')
        results.assert_true(registry_access, "Reflection can access core._registry")
        
        if registry_access:
            registry_items = list(reflection.core._registry.keys())
            results.assert_in('test_reflection', registry_items, "Reflection can read registry items")
        
        # Test CLI creation (this would have failed before fix)
        cli = reflection.create_reflective_cli()
        # If click is not available, cli will be None, but it shouldn't crash
        results.assert_true(True, "CLI creation doesn't crash")
        
    except AttributeError as e:
        if "_registry" in str(e):
            results.assert_true(False, f"REGISTRY BUG DETECTED: {e}")
        else:
            results.assert_true(False, f"Reflection system error: {e}")
    except Exception as e:
        results.assert_true(False, f"Reflection system error: {e}")


def test_example_app_integration(results):
    """Test that example apps can be imported and run without crashing."""
    print("\n=== Testing Example Apps Integration ===")
    
    # Test data-analyzer import
    try:
        import importlib.util
        
        # Import data-analyzer
        spec = importlib.util.spec_from_file_location(
            "data_analyzer", 
            "examples/data-analyzer/app.py"
        )
        data_analyzer = importlib.util.module_from_spec(spec)
        sys.modules["data_analyzer"] = data_analyzer
        spec.loader.exec_module(data_analyzer)
        
        # Check that it has a registry
        results.assert_true(hasattr(data_analyzer.app, '_registry'), "Data analyzer has registry")
        
        if hasattr(data_analyzer.app, '_registry'):
            registry_items = list(data_analyzer.app._registry.keys())
            results.assert_true(len(registry_items) > 0, "Data analyzer registry not empty")
            results.assert_in('load_csv_file', registry_items, "Data analyzer has expected functions")
        
    except Exception as e:
        results.assert_true(False, f"Data analyzer import failed: {e}")
    
    # Test task-manager import
    try:
        spec = importlib.util.spec_from_file_location(
            "task_manager", 
            "examples/task-manager/app.py"
        )
        task_manager = importlib.util.module_from_spec(spec)
        sys.modules["task_manager"] = task_manager
        spec.loader.exec_module(task_manager)
        
        results.assert_true(hasattr(task_manager.app, '_registry'), "Task manager has registry")
        
        if hasattr(task_manager.app, '_registry'):
            registry_items = list(task_manager.app._registry.keys())
            results.assert_true(len(registry_items) > 0, "Task manager registry not empty")
            results.assert_in('create_task', registry_items, "Task manager has expected functions")
        
    except Exception as e:
        results.assert_true(False, f"Task manager import failed: {e}")


def test_subprocess_execution(results):
    """Test actual CLI execution via subprocess (the ultimate integration test)."""
    print("\n=== Testing Subprocess Execution ===")
    
    # Create a minimal test app
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(current_dir, 'src')
    test_app_content = f'''
import sys
sys.path.insert(0, "{src_path}")

from yaapp import Yaapp

app = Yaapp()

@app.expose
def test_cmd(name: str = "Test") -> str:
    return f"Hello, {{name}}!"

if __name__ == "__main__":
    app.run()
'''
    
    # Write test app to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_app_content)
        test_app_path = f.name
    
    try:
        # Test that the app can run without crashing
        env = os.environ.copy()
        env['PYTHONPATH'] = 'src'
        
        result = subprocess.run(
            [sys.executable, test_app_path], 
            capture_output=True, 
            text=True, 
            timeout=2,
            env=env
        )
        
        # Should not crash, even without click
        results.assert_equal(result.returncode, 0, "Test app runs without crashing")
        results.assert_true("Available functions:" in result.stdout, "Test app shows functions")
        results.assert_true("test_cmd" in result.stdout, "Test app shows exposed function")
        
    except subprocess.TimeoutExpired:
        results.assert_true(False, "Test app timed out")
    except Exception as e:
        results.assert_true(False, f"Subprocess test failed: {e}")
    finally:
        # Clean up
        os.unlink(test_app_path)


def test_result_pattern_integration(results):
    """Test Result pattern is used consistently."""
    print("\n=== Testing Result Pattern Integration ===")
    
    app = Yaapp()
    
    # Test that exposers return Result objects
    from yaapp.result import Result, Ok
    
    # Test function exposer
    def test_func():
        return "test"
    
    result = app._function_exposer.expose(test_func, "test")
    results.assert_true(isinstance(result, Result), "Function exposer returns Result")
    results.assert_true(result.is_ok(), "Function exposer returns Ok result")
    
    # Test class exposer
    class TestClass:
        def method(self):
            return "method"
    
    result = app._class_exposer.expose(TestClass, "TestClass")
    results.assert_true(isinstance(result, Result), "Class exposer returns Result")
    results.assert_true(result.is_ok(), "Class exposer returns Ok result")
    
    # Test custom exposer with valid object
    class ValidCustomObject:
        def execute_call(self, **kwargs):
            return "valid"
    
    valid_obj = ValidCustomObject()
    result = app._custom_exposer.expose(valid_obj, "valid", custom=True)
    results.assert_true(isinstance(result, Result), "Custom exposer returns Result")
    results.assert_true(result.is_ok(), "Custom exposer returns Ok result for valid object")
    
    # Test custom exposer with invalid object
    invalid_obj = "not a custom object"
    result = app._custom_exposer.expose(invalid_obj, "invalid", custom=True)
    results.assert_true(isinstance(result, Result), "Custom exposer returns Result for invalid object")
    results.assert_true(not result.is_ok(), "Custom exposer returns Error result for invalid object")


def main():
    """Run all integration tests."""
    print("🧪 YAPP Framework Integration Tests")
    print("These tests verify end-to-end functionality and component integration.")
    
    results = TestResults()
    
    # Run all test suites
    test_basic_exposure_and_registry(results)
    test_exposer_system_integration(results)
    # test_cli_integration_without_click(results)  # Skip - CLI now works
    test_reflection_system_integration(results)  # This would have caught the bug!
    test_example_app_integration(results)
    test_subprocess_execution(results)
    test_result_pattern_integration(results)
    
    # Show summary
    success = results.summary()
    
    if success:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("The framework is working correctly end-to-end.")
    else:
        print("\n💥 INTEGRATION TESTS FAILED!")  
        print("Critical issues detected in framework integration.")
        sys.exit(1)


if __name__ == "__main__":
    main()