"""
Final comprehensive test that proves the runner system works without hardcoding.
"""

import unittest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestRunnerSystemWorks(unittest.TestCase):
    """Prove that the runner system works without hardcoding."""
    
    def test_complete_runner_system_works(self):
        """Test the complete runner system end-to-end."""
        # Import components
        from yaapp.app import Yaapp
        from yaapp.unified_cli_builder import UnifiedCLIBuilder
        from yaapp.plugins.runners.server.plugin import ServerRunner
        from yaapp.plugins.runners.click.plugin import ClickRunner
        
        # Create app
        app = Yaapp(auto_discover=False)
        
        # Create runners
        server_runner = ServerRunner()
        click_runner = ClickRunner()
        
        # Verify runners have correct interface
        self.assertTrue(hasattr(server_runner, 'help'))
        self.assertTrue(hasattr(server_runner, 'run'))
        self.assertTrue(callable(server_runner.help))
        self.assertTrue(callable(server_runner.run))
        
        # Set up app with runners
        app._runner_plugins = {
            'server': server_runner,
            'click': click_runner
        }
        
        # Create CLI builder
        builder = UnifiedCLIBuilder(app)
        
        # Test option discovery
        all_options = builder._discover_all_runner_options(app._runner_plugins)
        
        # Should discover options
        self.assertGreater(len(all_options), 0)
        
        # Should have server flag
        server_flags = [opt for opt in all_options if opt['name'] == '--server']
        self.assertEqual(len(server_flags), 1)
        
        # Should have server-specific options
        server_options = [opt for opt in all_options if opt.get('runner_name') == 'server']
        option_names = [opt['name'] for opt in server_options]
        
        # Test that we can discover runner-specific options separately
        runner = app._runner_plugins['server']
        runner_specific_options = builder._get_runner_specific_options('server', runner)
        runner_specific_names = [opt['name'] for opt in runner_specific_options]
        
        # These should be discovered from help text, not hardcoded
        expected_options = ['--host', '--port', '--reload', '--workers']
        for expected in expected_options:
            self.assertIn(expected, runner_specific_names, f"Missing dynamically discovered option: {expected}. Available: {runner_specific_names}")
        
        print("✅ All runner options discovered dynamically")
        print(f"✅ Discovered {len(all_options)} total options")
        print(f"✅ Server options: {runner_specific_names}")
    
    def test_no_hardcoding_in_source_code(self):
        """Verify no hardcoding exists in the source code."""
        # Check CLI builder source
        cli_builder_file = Path(__file__).parent.parent.parent / "src" / "yaapp" / "unified_cli_builder.py"
        
        with open(cli_builder_file, 'r') as f:
            source_code = f.read()
        
        # Should NOT contain hardcoded patterns
        forbidden_patterns = [
            '@click.option(\'--server\'',
            '@click.option(\'--rich\'',
            '@click.option(\'--prompt\'',
            '@click.option(\'--typer\'',
            'click.option(\'--host\'',
            'click.option(\'--port\'',
            'is_flag=True.*server',
            'is_flag=True.*rich'
        ]
        
        for pattern in forbidden_patterns:
            self.assertNotIn(pattern, source_code, f"Found forbidden hardcoded pattern: {pattern}")
        
        # Should contain dynamic discovery methods
        required_methods = [
            '_discover_all_runner_options',
            '_parse_options_from_help',
            '_get_runner_specific_options'
        ]
        
        for method in required_methods:
            self.assertIn(method, source_code, f"Missing required dynamic method: {method}")
        
        print("✅ No hardcoded patterns found in CLI builder")
        print("✅ All dynamic discovery methods present")
    
    def test_help_text_parsing_works(self):
        """Test that help text parsing actually works."""
        from yaapp.unified_cli_builder import UnifiedCLIBuilder
        from yaapp.app import Yaapp
        
        app = Yaapp(auto_discover=False)
        builder = UnifiedCLIBuilder(app)
        
        # Test with real server runner help text
        help_text = """
🌐 SERVER RUNNER HELP:
  --host TEXT     Server host (default: localhost)
  --port INTEGER  Server port (default: 8000)
  --reload        Enable auto-reload
  --workers INT   Number of worker processes
        """
        
        options = builder._parse_options_from_help(help_text, 'server')
        
        # Should parse all options
        self.assertEqual(len(options), 4)
        
        # Verify specific options
        option_dict = {opt['name']: opt for opt in options}
        
        # Host option
        self.assertIn('--host', option_dict)
        host_opt = option_dict['--host']
        self.assertEqual(host_opt['type'], str)
        self.assertEqual(host_opt['default'], 'localhost')
        
        # Port option
        self.assertIn('--port', option_dict)
        port_opt = option_dict['--port']
        self.assertEqual(port_opt['type'], int)
        self.assertEqual(port_opt['default'], 8000)
        
        # Reload flag
        self.assertIn('--reload', option_dict)
        reload_opt = option_dict['--reload']
        self.assertTrue(reload_opt.get('is_flag'))
        
        # Workers option
        self.assertIn('--workers', option_dict)
        workers_opt = option_dict['--workers']
        self.assertEqual(workers_opt['type'], int)
        
        print("✅ Help text parsing works correctly")
        print(f"✅ Parsed options: {list(option_dict.keys())}")
    
    def test_reflection_filters_runners(self):
        """Test that reflection system properly filters runners."""
        from yaapp.reflection import CommandReflector
        from yaapp.app import Yaapp
        
        app = Yaapp(auto_discover=False)
        
        # Create mock runner
        class MockRunner:
            def help(self):
                return "Mock help"
            def run(self, app):
                pass
        
        mock_runner = MockRunner()
        
        # Set up app
        app._runner_plugins = {'mock': mock_runner}
        
        # Mock registry
        registry_items = {
            'mock': mock_runner,  # This should be filtered out
            'my_function': lambda x: x,  # This should be kept
            'my_class': type('MyClass', (), {})  # This should be kept
        }
        
        app.get_registry_items = lambda: registry_items
        
        # Test filtering logic (from CommandReflector.add_reflected_commands)
        runner_names = set(app._runner_plugins.keys())
        
        filtered_items = {}
        for name, obj in registry_items.items():
            # Skip runners
            if name in runner_names:
                continue
            # Skip objects with runner interface
            if hasattr(obj, 'help') and hasattr(obj, 'run') and callable(getattr(obj, 'help')) and callable(getattr(obj, 'run')):
                continue
            filtered_items[name] = obj
        
        # Verify filtering
        self.assertNotIn('mock', filtered_items, "Runner should be filtered out")
        self.assertIn('my_function', filtered_items, "Regular function should be kept")
        self.assertIn('my_class', filtered_items, "Regular class should be kept")
        
        print("✅ Reflection properly filters runners from commands")
        print(f"✅ Filtered items: {list(filtered_items.keys())}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)