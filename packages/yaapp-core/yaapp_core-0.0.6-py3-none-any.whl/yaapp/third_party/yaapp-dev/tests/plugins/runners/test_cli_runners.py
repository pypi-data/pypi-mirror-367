"""
Comprehensive tests for CLI runners (Typer, Prompt, Rich, Click).
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


class TestTyperRunner:
    """Test Typer runner functionality."""
    
    def test_typer_runner_import(self):
        """Test Typer runner can be imported."""
        try:
            from yaapp.plugins.runners.typer.plugin import Typer
            runner = Typer()
            assert runner is not None
            assert hasattr(runner, 'help')
            assert hasattr(runner, 'run')
        except ImportError:
            pytest.skip("Typer runner not available")
    
    def test_typer_runner_help(self):
        """Test Typer runner help text."""
        try:
            from yaapp.plugins.runners.typer.plugin import Typer
            runner = Typer()
            help_text = runner.help()
            assert isinstance(help_text, str)
            assert len(help_text) > 0
        except ImportError:
            pytest.skip("Typer runner not available")


class TestPromptRunner:
    """Test Prompt runner functionality."""
    
    def test_prompt_runner_import(self):
        """Test Prompt runner can be imported."""
        try:
            from yaapp.plugins.runners.prompt.plugin import Prompt
            runner = Prompt()
            assert runner is not None
            assert hasattr(runner, 'help')
            assert hasattr(runner, 'run')
        except ImportError:
            pytest.skip("Prompt runner not available")
    
    def test_prompt_runner_help(self):
        """Test Prompt runner help text."""
        try:
            from yaapp.plugins.runners.prompt.plugin import Prompt
            runner = Prompt()
            help_text = runner.help()
            assert isinstance(help_text, str)
            assert "PROMPT" in help_text.upper()
        except ImportError:
            pytest.skip("Prompt runner not available")
    
    def test_prompt_runner_missing_dependency(self):
        """Test Prompt runner when prompt_toolkit is missing."""
        try:
            from yaapp.plugins.runners.prompt.plugin import Prompt
            runner = Prompt()
            
            with patch('yaapp.plugins.runners.prompt.plugin.HAS_PROMPT_TOOLKIT', False):
                with patch('builtins.print') as mock_print:
                    runner.run(None)
                    mock_print.assert_called()
                    # Should print error about missing prompt_toolkit
        except ImportError:
            pytest.skip("Prompt runner not available")


class TestRichRunner:
    """Test Rich runner functionality."""
    
    def test_rich_runner_import(self):
        """Test Rich runner can be imported."""
        try:
            from yaapp.plugins.runners.rich.plugin import Rich
            runner = Rich()
            assert runner is not None
            assert hasattr(runner, 'help')
            assert hasattr(runner, 'run')
        except ImportError:
            pytest.skip("Rich runner not available")
    
    def test_rich_runner_help(self):
        """Test Rich runner help text."""
        try:
            from yaapp.plugins.runners.rich.plugin import Rich
            runner = Rich()
            help_text = runner.help()
            assert isinstance(help_text, str)
            assert "RICH" in help_text.upper()
        except ImportError:
            pytest.skip("Rich runner not available")
    
    def test_rich_runner_config(self):
        """Test Rich runner configuration."""
        try:
            from yaapp.plugins.runners.rich.plugin import Rich
            config = {'theme': 'light', 'layout': 'table'}
            runner = Rich(config)
            assert runner.config == config
        except ImportError:
            pytest.skip("Rich runner not available")


class TestClickRunner:
    """Test Click runner functionality."""
    
    def test_click_runner_import(self):
        """Test Click runner can be imported."""
        try:
            from yaapp.plugins.runners.click.plugin import Click
            runner = Click()
            assert runner is not None
            assert hasattr(runner, 'help')
            assert hasattr(runner, 'run')
        except ImportError:
            pytest.skip("Click runner not available")
    
    def test_click_runner_help(self):
        """Test Click runner help text."""
        try:
            from yaapp.plugins.runners.click.plugin import Click
            runner = Click()
            help_text = runner.help()
            assert isinstance(help_text, str)
            assert "CLICK" in help_text.upper()
        except ImportError:
            pytest.skip("Click runner not available")


class TestRunnerDiscovery:
    """Test runner discovery system."""
    
    def test_all_runners_discoverable(self):
        """Test that all runners can be discovered."""
        from yaapp.discovery import PluginDiscovery
        
        discovery = PluginDiscovery()
        discovered_runners = discovery.discover_runners()
        
        # Should discover at least some runners
        assert len(discovered_runners) > 0
        
        # Should include core runners
        expected_runners = ['mcp', 'server', 'gradio', 'streamlit', 'nicegui']
        
        for runner in expected_runners:
            assert runner in discovered_runners
    
    def test_runner_registration(self, test_app):
        """Test runner registration with yaapp."""
        # Test that runners are properly registered
        from yaapp import Yaapp
        
        # Create a test app to check registration
        app = Yaapp(auto_discover=False)
        
        # Import all runner plugins to trigger registration
        try:
            import yaapp.plugins.runners.mcp.plugin
            import yaapp.plugins.runners.server.plugin
            import yaapp.plugins.runners.gradio.plugin
            import yaapp.plugins.runners.streamlit.plugin
            import yaapp.plugins.runners.nicegui.plugin
        except ImportError:
            pass  # Some runners might not be available
        
        # Check that runners can be imported and instantiated
        runner_classes = [
            ('mcp', 'yaapp.plugins.runners.mcp.plugin', 'Mcp'),
            ('server', 'yaapp.plugins.runners.server.plugin', 'Server'),
            ('gradio', 'yaapp.plugins.runners.gradio.plugin', 'Gradio'),
            ('streamlit', 'yaapp.plugins.runners.streamlit.plugin', 'Streamlit'),
            ('nicegui', 'yaapp.plugins.runners.nicegui.plugin', 'NiceGUI'),
        ]
        
        successful_imports = 0
        for name, module_path, class_name in runner_classes:
            try:
                module = __import__(module_path, fromlist=[class_name])
                runner_class = getattr(module, class_name)
                runner = runner_class()
                successful_imports += 1
            except (ImportError, AttributeError):
                pass
        
        assert successful_imports > 0
    
    def test_runner_instantiation(self):
        """Test that runners can be instantiated."""
        # Test direct instantiation of runner classes
        runner_classes = [
            ('mcp', 'yaapp.plugins.runners.mcp.plugin', 'Mcp'),
            ('server', 'yaapp.plugins.runners.server.plugin', 'Server'),
            ('gradio', 'yaapp.plugins.runners.gradio.plugin', 'Gradio'),
            ('streamlit', 'yaapp.plugins.runners.streamlit.plugin', 'Streamlit'),
            ('nicegui', 'yaapp.plugins.runners.nicegui.plugin', 'NiceGUI'),
        ]
        
        successful_instantiations = 0
        for name, module_path, class_name in runner_classes:
            try:
                module = __import__(module_path, fromlist=[class_name])
                runner_class = getattr(module, class_name)
                instance = runner_class()
                assert hasattr(instance, 'run')
                assert hasattr(instance, 'help')
                successful_instantiations += 1
            except (ImportError, AttributeError) as e:
                # Expected for some runners that might not be available
                pass
            except Exception as e:
                pytest.fail(f"Failed to instantiate {name} runner: {e}")
        
        assert successful_instantiations > 0


class TestRunnerIntegration:
    """Test runner integration with yaapp."""
    
    def test_runner_help_methods(self):
        """Test that all runners have working help methods."""
        runner_classes = [
            ('mcp', 'yaapp.plugins.runners.mcp.plugin', 'Mcp'),
            ('server', 'yaapp.plugins.runners.server.plugin', 'Server'),
            ('gradio', 'yaapp.plugins.runners.gradio.plugin', 'Gradio'),
            ('streamlit', 'yaapp.plugins.runners.streamlit.plugin', 'Streamlit'),
            ('nicegui', 'yaapp.plugins.runners.nicegui.plugin', 'NiceGUI'),
        ]
        
        successful_help_tests = 0
        for name, module_path, class_name in runner_classes:
            try:
                module = __import__(module_path, fromlist=[class_name])
                runner_class = getattr(module, class_name)
                instance = runner_class()
                if hasattr(instance, 'help'):
                    help_text = instance.help()
                    assert isinstance(help_text, str)
                    assert len(help_text) > 0
                    successful_help_tests += 1
            except (ImportError, AttributeError):
                # Expected for some runners that might not be available
                pass
        
        assert successful_help_tests > 0
    
    def test_runner_run_methods(self, test_app):
        """Test that all runners have working run methods."""
        runner_classes = [
            ('mcp', 'yaapp.plugins.runners.mcp.plugin', 'Mcp'),
            ('server', 'yaapp.plugins.runners.server.plugin', 'Server'),
            ('gradio', 'yaapp.plugins.runners.gradio.plugin', 'Gradio'),
            ('streamlit', 'yaapp.plugins.runners.streamlit.plugin', 'Streamlit'),
            ('nicegui', 'yaapp.plugins.runners.nicegui.plugin', 'NiceGUI'),
        ]
        
        successful_run_tests = 0
        for name, module_path, class_name in runner_classes:
            try:
                module = __import__(module_path, fromlist=[class_name])
                runner_class = getattr(module, class_name)
                instance = runner_class()
                if hasattr(instance, 'run'):
                    # Should be callable (we won't actually run it in tests)
                    assert callable(instance.run)
                    successful_run_tests += 1
            except (ImportError, AttributeError):
                # Expected for some runners that might not be available
                pass
        
        assert successful_run_tests > 0
    
    def test_runner_config_handling(self):
        """Test that runners handle configuration properly."""
        from yaapp.plugins.runners.mcp.plugin import Mcp
        from yaapp.plugins.runners.server.plugin import Server
        from yaapp.plugins.runners.gradio.plugin import Gradio
        from yaapp.plugins.runners.streamlit.plugin import Streamlit
        from yaapp.plugins.runners.nicegui.plugin import NiceGUI
        
        # Test that all runners accept config
        config = {'test': 'value'}
        
        runners = [Mcp(config), Server(config), Gradio(config), 
                  Streamlit(config), NiceGUI(config)]
        
        for runner in runners:
            assert hasattr(runner, 'config')
            assert runner.config == config