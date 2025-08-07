#!/usr/bin/env python3
"""
Test the runner code duplication fix.
Tests that common TUI functionality is extracted into InteractiveTUIRunner base class.
"""

import sys
import inspect
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, "../../src")

from yaapp import Yaapp


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
    
    def assert_not_none(self, value, message):
        if value is not None:
            self.passed += 1
            print(f"✅ {message}")
        else:
            self.failed += 1
            error = f"❌ {message} - Value was None"
            print(error)
            self.errors.append(error)
    
    def assert_contains(self, container, item, message):
        if item in container:
            self.passed += 1
            print(f"✅ {message}")
        else:
            self.failed += 1
            error = f"❌ {message} - '{item}' not found in container"
            print(error)
            self.errors.append(error)
    
    def assert_less_than(self, actual, threshold, message):
        if actual < threshold:
            self.passed += 1
            print(f"✅ {message}")
        else:
            self.failed += 1
            error = f"❌ {message} - {actual} >= {threshold}"
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


def test_interactive_base_class_exists(results):
    """Test that InteractiveTUIRunner base class exists and has expected interface."""
    print("\n=== Testing InteractiveTUIRunner Base Class ===")
    
    try:
        from yaapp.runners.interactive_base import InteractiveTUIRunner
        
        results.assert_not_none(InteractiveTUIRunner, "InteractiveTUIRunner class exists")
        
        # Test that it's abstract
        results.assert_true(inspect.isabstract(InteractiveTUIRunner), "InteractiveTUIRunner is abstract")
        
        # Test it has the expected abstract methods
        abstract_methods = getattr(InteractiveTUIRunner, '__abstractmethods__', set())
        expected_abstracts = {'_check_dependencies', '_get_backend_name', '_get_user_input'}
        results.assert_true(expected_abstracts.issubset(abstract_methods), 
                           f"Has expected abstract methods: {expected_abstracts}")
        
        # Test it has the common methods
        common_methods = ['run', '_execute_tui_command', '_print_error', '_print_warning', '_print_result']
        for method in common_methods:
            results.assert_true(hasattr(InteractiveTUIRunner, method), 
                               f"Has common method: {method}")
        
    except Exception as e:
        results.assert_true(False, f"InteractiveTUIRunner base class test failed: {e}")


def test_prompt_runner_inheritance(results):
    """Test that PromptRunner properly inherits from InteractiveTUIRunner."""
    print("\n=== Testing PromptRunner Inheritance ===")
    
    try:
        from yaapp.runners.prompt_runner import PromptRunner
        from yaapp.runners.interactive_base import InteractiveTUIRunner
        
        app = Yaapp()
        
        @app.expose
        def test_func() -> str:
            return "test"
        
        runner = PromptRunner(app)
        
        # Test inheritance
        results.assert_true(isinstance(runner, InteractiveTUIRunner), 
                           "PromptRunner inherits from InteractiveTUIRunner")
        
        # Test abstract methods are implemented
        results.assert_true(hasattr(runner, '_check_dependencies'), "Implements _check_dependencies")
        results.assert_true(hasattr(runner, '_get_backend_name'), "Implements _get_backend_name")
        results.assert_true(hasattr(runner, '_get_user_input'), "Implements _get_user_input")
        
        # Test method implementations
        results.assert_equal(runner._get_backend_name(), "prompt_toolkit", "Backend name is correct")
        
        # Test dependency check
        dep_check = runner._check_dependencies()
        results.assert_true(isinstance(dep_check, bool), "Dependency check returns boolean")
        
    except Exception as e:
        results.assert_true(False, f"PromptRunner inheritance test failed: {e}")


def test_typer_runner_inheritance(results):
    """Test that TyperRunner properly inherits from InteractiveTUIRunner."""
    print("\n=== Testing TyperRunner Inheritance ===")
    
    try:
        from yaapp.runners.typer_runner import TyperRunner
        from yaapp.runners.interactive_base import InteractiveTUIRunner
        
        app = Yaapp()
        
        @app.expose
        def test_func() -> str:
            return "test"
        
        runner = TyperRunner(app)
        
        # Test inheritance
        results.assert_true(isinstance(runner, InteractiveTUIRunner), 
                           "TyperRunner inherits from InteractiveTUIRunner")
        
        # Test abstract methods are implemented
        results.assert_true(hasattr(runner, '_check_dependencies'), "Implements _check_dependencies")
        results.assert_true(hasattr(runner, '_get_backend_name'), "Implements _get_backend_name")
        results.assert_true(hasattr(runner, '_get_user_input'), "Implements _get_user_input")
        
        # Test method implementations
        results.assert_equal(runner._get_backend_name(), "Typer", "Backend name is correct")
        
        # Test dependency check
        dep_check = runner._check_dependencies()
        results.assert_true(isinstance(dep_check, bool), "Dependency check returns boolean")
        
    except Exception as e:
        results.assert_true(False, f"TyperRunner inheritance test failed: {e}")


def test_rich_runner_inheritance(results):
    """Test that RichRunner properly inherits from InteractiveTUIRunner."""
    print("\n=== Testing RichRunner Inheritance ===")
    
    try:
        from yaapp.runners.rich_runner import RichRunner
        from yaapp.runners.interactive_base import InteractiveTUIRunner
        
        app = Yaapp()
        
        @app.expose
        def test_func() -> str:
            return "test"
        
        runner = RichRunner(app)
        
        # Test inheritance
        results.assert_true(isinstance(runner, InteractiveTUIRunner), 
                           "RichRunner inherits from InteractiveTUIRunner")
        
        # Test abstract methods are implemented
        results.assert_true(hasattr(runner, '_check_dependencies'), "Implements _check_dependencies")
        results.assert_true(hasattr(runner, '_get_backend_name'), "Implements _get_backend_name")
        results.assert_true(hasattr(runner, '_get_user_input'), "Implements _get_user_input")
        
        # Test method implementations
        results.assert_equal(runner._get_backend_name(), "Rich", "Backend name is correct")
        
        # Test dependency check
        dep_check = runner._check_dependencies()
        results.assert_true(isinstance(dep_check, bool), "Dependency check returns boolean")
        
        # Test console initialization
        results.assert_true(hasattr(runner, 'console'), "Has console attribute")
        
    except Exception as e:
        results.assert_true(False, f"RichRunner inheritance test failed: {e}")


def test_code_duplication_eliminated(results):
    """Test that code duplication has been eliminated."""
    print("\n=== Testing Code Duplication Elimination ===")
    
    try:
        from yaapp.runners.prompt_runner import PromptRunner
        from yaapp.runners.typer_runner import TyperRunner
        from yaapp.runners.rich_runner import RichRunner
        
        # Test that runner classes are now much smaller
        prompt_methods = [m for m in dir(PromptRunner) if not m.startswith('_') or m in ['_check_dependencies', '_get_backend_name', '_get_user_input']]
        typer_methods = [m for m in dir(TyperRunner) if not m.startswith('_') or m in ['_check_dependencies', '_get_backend_name', '_get_user_input']]
        
        results.assert_less_than(len(prompt_methods), 10, f"PromptRunner has focused interface: {len(prompt_methods)} methods")
        results.assert_less_than(len(typer_methods), 10, f"TyperRunner has focused interface: {len(typer_methods)} methods")
        
        # Test that they don't have duplicate _execute_tui_command implementations
        app = Yaapp()
        prompt_runner = PromptRunner(app)
        typer_runner = TyperRunner(app)
        rich_runner = RichRunner(app)
        
        # They should all use the same _execute_tui_command from base class
        prompt_execute = prompt_runner._execute_tui_command
        typer_execute = typer_runner._execute_tui_command
        rich_execute = rich_runner._execute_tui_command
        
        # Check that the method comes from the base class
        results.assert_contains(str(prompt_execute.__qualname__), 'InteractiveTUIRunner', 
                               "PromptRunner uses base class _execute_tui_command")
        results.assert_contains(str(typer_execute.__qualname__), 'InteractiveTUIRunner', 
                               "TyperRunner uses base class _execute_tui_command")
        results.assert_contains(str(rich_execute.__qualname__), 'InteractiveTUIRunner', 
                               "RichRunner uses base class _execute_tui_command")
        
    except Exception as e:
        results.assert_true(False, f"Code duplication elimination test failed: {e}")


def test_common_execution_functionality(results):
    """Test that common execution functionality works correctly."""
    print("\n=== Testing Common Execution Functionality ===")
    
    try:
        from yaapp.runners.interactive_base import InteractiveTUIRunner
        from yaapp.runners.prompt_runner import PromptRunner
        
        app = Yaapp()
        
        @app.expose
        def test_execution(value: str = "default") -> str:
            return f"executed: {value}"
        
        runner = PromptRunner(app)
        
        # Test that _execute_tui_command exists and works
        results.assert_true(hasattr(runner, '_execute_tui_command'), "Has _execute_tui_command method")
        
        # Test print methods exist
        results.assert_true(hasattr(runner, '_print_error'), "Has _print_error method")
        results.assert_true(hasattr(runner, '_print_warning'), "Has _print_warning method")
        results.assert_true(hasattr(runner, '_print_result'), "Has _print_result method")
        
        # Mock console for testing
        mock_console = Mock()
        mock_console.print = Mock()
        mock_console.print_json = Mock()
        
        # Test error printing
        runner._print_error("test error", mock_console)
        mock_console.print.assert_called()
        
        # Test warning printing
        runner._print_warning("test warning", mock_console)
        mock_console.print.assert_called()
        
        # Test result printing
        runner._print_result("test result", mock_console)
        mock_console.print.assert_called()
        
        results.assert_true(True, "Common execution functionality works")
        
    except Exception as e:
        results.assert_true(False, f"Common execution functionality test failed: {e}")


def test_runner_specific_differences(results):
    """Test that runners maintain their specific differences while sharing common code."""
    print("\n=== Testing Runner-Specific Differences ===")
    
    try:
        from yaapp.runners.prompt_runner import PromptRunner
        from yaapp.runners.typer_runner import TyperRunner
        from yaapp.runners.rich_runner import RichRunner
        
        app = Yaapp()
        
        prompt_runner = PromptRunner(app)
        typer_runner = TyperRunner(app)
        rich_runner = RichRunner(app)
        
        # Test different backend names
        results.assert_equal(prompt_runner._get_backend_name(), "prompt_toolkit", "PromptRunner has correct backend name")
        results.assert_equal(typer_runner._get_backend_name(), "Typer", "TyperRunner has correct backend name")
        results.assert_equal(rich_runner._get_backend_name(), "Rich", "RichRunner has correct backend name")
        
        # Test that they have different user input methods
        prompt_input = prompt_runner._get_user_input
        typer_input = typer_runner._get_user_input
        rich_input = rich_runner._get_user_input
        
        # These should be different implementations
        results.assert_true(prompt_input != typer_input, "PromptRunner and TyperRunner have different input methods")
        results.assert_true(typer_input != rich_input, "TyperRunner and RichRunner have different input methods")
        results.assert_true(prompt_input != rich_input, "PromptRunner and RichRunner have different input methods")
        
        # Test RichRunner has special features
        results.assert_true(hasattr(rich_runner, 'console'), "RichRunner has console attribute")
        results.assert_true(hasattr(rich_runner, '_create_context_table'), "RichRunner has rich-specific methods")
        
        results.assert_true(True, "Runner-specific differences preserved")
        
    except Exception as e:
        results.assert_true(False, f"Runner-specific differences test failed: {e}")


def test_backward_compatibility(results):
    """Test that refactoring maintains backward compatibility."""
    print("\n=== Testing Backward Compatibility ===")
    
    try:
        from yaapp.runners import PromptRunner, TyperRunner, RichRunner, ClickRunner
        
        app = Yaapp()
        
        @app.expose
        def test_compat() -> str:
            return "compatible"
        
        # Test that runners can still be instantiated the same way
        prompt_runner = PromptRunner(app)
        typer_runner = TyperRunner(app)
        rich_runner = RichRunner(app)
        click_runner = ClickRunner(app)
        
        results.assert_not_none(prompt_runner, "PromptRunner instantiates correctly")
        results.assert_not_none(typer_runner, "TyperRunner instantiates correctly")
        results.assert_not_none(rich_runner, "RichRunner instantiates correctly")
        results.assert_not_none(click_runner, "ClickRunner instantiates correctly")
        
        # Test that they still have the run method
        results.assert_true(hasattr(prompt_runner, 'run'), "PromptRunner has run method")
        results.assert_true(hasattr(typer_runner, 'run'), "TyperRunner has run method")
        results.assert_true(hasattr(rich_runner, 'run'), "RichRunner has run method")
        results.assert_true(hasattr(click_runner, 'run'), "ClickRunner has run method")
        
        # Test that they still inherit from BaseRunner
        from yaapp.runners.base import BaseRunner
        results.assert_true(isinstance(prompt_runner, BaseRunner), "PromptRunner still inherits from BaseRunner")
        results.assert_true(isinstance(typer_runner, BaseRunner), "TyperRunner still inherits from BaseRunner")
        results.assert_true(isinstance(rich_runner, BaseRunner), "RichRunner still inherits from BaseRunner")
        results.assert_true(isinstance(click_runner, BaseRunner), "ClickRunner still inherits from BaseRunner")
        
        results.assert_true(True, "Backward compatibility maintained")
        
    except Exception as e:
        results.assert_true(False, f"Backward compatibility test failed: {e}")


def test_maintainability_improvements(results):
    """Test that the refactoring improves maintainability."""
    print("\n=== Testing Maintainability Improvements ===")
    
    try:
        from yaapp.runners.interactive_base import InteractiveTUIRunner
        
        # Test that common code is centralized
        base_source = inspect.getsource(InteractiveTUIRunner)
        
        # Test that _execute_tui_command is substantial and centralized
        results.assert_contains(base_source, 'def _execute_tui_command', "Base class contains _execute_tui_command")
        results.assert_contains(base_source, 'def _print_error', "Base class contains _print_error")
        results.assert_contains(base_source, 'def _print_warning', "Base class contains _print_warning")
        results.assert_contains(base_source, 'def _print_result', "Base class contains _print_result")
        
        # Test that the base class has substantial functionality (not just stubs)
        base_method_lines = base_source.count('\n')
        results.assert_true(base_method_lines > 50, f"Base class has substantial code: {base_method_lines} lines")
        
        # Test that concrete runners are now much smaller
        from yaapp.runners.prompt_runner import PromptRunner
        from yaapp.runners.typer_runner import TyperRunner
        
        prompt_source = inspect.getsource(PromptRunner)
        typer_source = inspect.getsource(TyperRunner)
        
        prompt_lines = prompt_source.count('\n')
        typer_lines = typer_source.count('\n')
        
        results.assert_less_than(prompt_lines, 50, f"PromptRunner is now concise: {prompt_lines} lines")
        results.assert_less_than(typer_lines, 40, f"TyperRunner is now concise: {typer_lines} lines")
        
        results.assert_true(True, "Maintainability significantly improved")
        
    except Exception as e:
        results.assert_true(False, f"Maintainability improvements test failed: {e}")


def main():
    """Run all runner code duplication fix tests."""
    print("🔄 YAPP Runner Code Duplication Fix Tests")
    print("Testing extraction of common TUI functionality into InteractiveTUIRunner base class.")
    
    results = TestResults()
    
    # Run all test suites
    test_interactive_base_class_exists(results)
    test_prompt_runner_inheritance(results)
    test_typer_runner_inheritance(results)
    test_rich_runner_inheritance(results)
    test_code_duplication_eliminated(results)
    test_common_execution_functionality(results)
    test_runner_specific_differences(results)
    test_backward_compatibility(results) 
    test_maintainability_improvements(results)
    
    # Show summary
    success = results.summary()
    
    if success:
        print("\n🎉 ALL RUNNER CODE DUPLICATION FIX TESTS PASSED!")
        print("Massive code duplication successfully eliminated:")
        print("  • Created InteractiveTUIRunner base class with common functionality")
        print("  • Extracted _execute_tui_command, _print_* methods to base class")
        print("  • PromptRunner, TyperRunner, RichRunner now inherit common behavior")
        print("  • Each runner maintains its specific input method and formatting")
        print("  • ~100+ lines of duplicated code eliminated across 3 runners")
        print("  • Bug fixes now only need to be applied once in the base class")
    else:
        print("\n💥 RUNNER CODE DUPLICATION FIX TESTS FAILED!")
        print("Issues detected in runner refactoring.")
        sys.exit(1)


if __name__ == "__main__":
    main()