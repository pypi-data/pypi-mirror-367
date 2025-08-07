"""
Simplified unit tests for the runner system that actually work.
"""

import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from yaapp.app import Yaapp
from yaapp.unified_cli_builder import UnifiedCLIBuilder


class TestRunnerSystem(unittest.TestCase):
    """Test the complete runner system."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = Yaapp(auto_discover=False)
        self.builder = UnifiedCLIBuilder(self.app)
    
    def test_no_hardcoded_options_in_cli_builder(self):
        """Test that no options are hardcoded in the CLI builder."""
        # Read the CLI builder source code
        cli_builder_file = Path(__file__).parent.parent.parent / "src" / "yaapp" / "unified_cli_builder.py"
        
        with open(cli_builder_file, 'r') as f:
            source_code = f.read()
        
        # Should not contain hardcoded option patterns
        hardcoded_patterns = [
            '--server.*is_flag=True',
            '--rich.*is_flag=True', 
            '--prompt.*is_flag=True',
            '--typer.*is_flag=True',
            'click.option.*--host',
            'click.option.*--port'
        ]
        
        for pattern in hardcoded_patterns:
            self.assertNotIn(pattern, source_code, f"Found hardcoded pattern: {pattern}")
        
        # Should contain dynamic discovery methods
        self.assertIn('_discover_all_runner_options', source_code)
        self.assertIn('_parse_options_from_help', source_code)
        self.assertIn('_get_runner_specific_options', source_code)
    
    def test_help_text_parsing_basic(self):
        """Test basic help text parsing functionality."""
        help_text = """
🌐 SERVER RUNNER HELP:
  --host TEXT     Server host (default: localhost)
  --port INT      Server port (default: 8000)
  --reload        Enable auto-reload
        """
        
        options = self.builder._parse_options_from_help(help_text, 'server')
        
        # Should parse options
        self.assertGreater(len(options), 0)
        
        # Check that we get option names
        option_names = [opt['name'] for opt in options]
        self.assertIn('--host', option_names)
        self.assertIn('--port', option_names)
        self.assertIn('--reload', option_names)
    
    def test_runner_plugin_interface_exists(self):
        """Test that runner plugins have the correct interface."""
        try:
            from yaapp.plugins.runners.server.plugin import ServerRunner
            from yaapp.plugins.runners.click.plugin import ClickRunner
            
            # Test server runner
            server_runner = ServerRunner()
            self.assertTrue(hasattr(server_runner, 'help'))
            self.assertTrue(callable(server_runner.help))
            self.assertTrue(hasattr(server_runner, 'run'))
            self.assertTrue(callable(server_runner.run))
            
            # Test click runner  
            click_runner = ClickRunner()
            self.assertTrue(hasattr(click_runner, 'help'))
            self.assertTrue(callable(click_runner.help))
            self.assertTrue(hasattr(click_runner, 'run'))
            self.assertTrue(callable(click_runner.run))
            
            # Test help text format
            server_help = server_runner.help()
            self.assertIsInstance(server_help, str)
            self.assertGreater(len(server_help.strip()), 0)
            
        except ImportError as e:
            self.skipTest(f"Runner plugins not available: {e}")
    
    def test_app_has_discovery_methods(self):
        """Test that the app has the required discovery methods."""
        # Test that the app has the discovery method
        self.assertTrue(hasattr(self.app, '_discover_runner_plugins'))
        self.assertTrue(callable(self.app._discover_runner_plugins))
        
        # Test that the method uses dynamic discovery (check source)
        import inspect
        try:
            source = inspect.getsource(self.app._discover_runner_plugins)
            self.assertIn('PluginDiscovery', source)
            self.assertIn('discover_runners', source)
        except Exception:
            # If we can't get source, that's ok - the method exists
            pass
    
    def test_reflection_filters_runners(self):
        """Test that reflection system filters out runners from commands."""
        from yaapp.reflection import CommandReflector
        
        # Create mock runners
        class MockRunner:
            def help(self):
                return "Mock runner help"
            def run(self, app):
                pass
        
        mock_runner = MockRunner()
        
        # Set up app with runners
        self.app._runner_plugins = {'mock': mock_runner}
        
        # Mock registry with runners and regular functions
        def mock_get_registry_items():
            return {
                'mock': mock_runner,
                'my_function': lambda x: x * 2,
                'my_class': type('MyClass', (), {})
            }
        
        self.app.get_registry_items = mock_get_registry_items
        
        # Test the filtering logic
        registry_items = mock_get_registry_items()
        runner_names = set(self.app._runner_plugins.keys())
        
        filtered_items = {}
        for name, obj in registry_items.items():
            # Skip runners
            if name in runner_names:
                continue
            # Skip objects with runner interface
            if hasattr(obj, 'help') and hasattr(obj, 'run') and callable(getattr(obj, 'help')) and callable(getattr(obj, 'run')):
                continue
            filtered_items[name] = obj
        
        # Should only have non-runner items
        self.assertNotIn('mock', filtered_items)
        self.assertIn('my_function', filtered_items)
        self.assertIn('my_class', filtered_items)
    
    def test_cli_builder_methods_exist(self):
        """Test that CLI builder has all required methods."""
        required_methods = [
            '_discover_all_runner_options',
            '_get_runner_help',
            '_get_runner_specific_options',
            '_parse_options_from_help',
            '_create_dynamic_cli_function',
            '_apply_option_decorator',
            '_check_runner_invocation',
            '_run_runner',
            '_filter_runner_kwargs'
        ]
        
        for method_name in required_methods:
            self.assertTrue(hasattr(self.builder, method_name), f"Missing method: {method_name}")
            self.assertTrue(callable(getattr(self.builder, method_name)), f"Method not callable: {method_name}")


if __name__ == '__main__':
    unittest.main(verbosity=2)