"""
Comprehensive tests for NiceGUI runner (disabled).
"""

import pytest
from unittest.mock import patch

from yaapp.plugins.runners.nicegui.plugin import NiceGUI


class TestNiceGUIRunner:
    """Test NiceGUI runner functionality."""
    
    def test_nicegui_runner_creation(self):
        """Test NiceGUI runner can be created."""
        runner = NiceGUI()
        assert runner is not None
        assert hasattr(runner, 'help')
        assert hasattr(runner, 'run')
    
    def test_nicegui_runner_help(self):
        """Test NiceGUI runner help text."""
        runner = NiceGUI()
        help_text = runner.help()
        
        assert "NICEGUI RUNNER HELP" in help_text
        assert "--host" in help_text
        assert "--port" in help_text
    
    def test_nicegui_runner_config(self):
        """Test NiceGUI runner configuration."""
        config = {
            'host': '0.0.0.0',
            'port': 9090
        }
        runner = NiceGUI(config)
        assert runner.config == config
    
    def test_nicegui_missing_dependency(self):
        """Test NiceGUI runner when nicegui is not installed."""
        runner = NiceGUI()
        
        with patch('yaapp.plugins.runners.nicegui.plugin.HAS_NICEGUI', False):
            with patch('builtins.print') as mock_print:
                runner.run(None)
                mock_print.assert_called()
                # Should print error about missing nicegui
    
    def test_nicegui_disabled_message(self, test_app):
        """Test NiceGUI runner shows disabled message."""
        runner = NiceGUI()
        
        with patch('yaapp.plugins.runners.nicegui.plugin.HAS_NICEGUI', True):
            with patch('builtins.print') as mock_print:
                runner.run(test_app)
                
                # Should print disabled message
                mock_print.assert_called()
                
                # Check that it mentions the reason for disabling
                calls = [str(call) for call in mock_print.call_args_list]
                disabled_mentioned = any("Disabled" in call for call in calls)
                assert disabled_mentioned
                
                # Should mention alternatives
                alternatives_mentioned = any("gradio" in call.lower() for call in calls)
                assert alternatives_mentioned
    
    def test_nicegui_alternatives_suggested(self, test_app):
        """Test NiceGUI runner suggests alternatives."""
        runner = NiceGUI()
        
        with patch('yaapp.plugins.runners.nicegui.plugin.HAS_NICEGUI', True):
            with patch('builtins.print') as mock_print:
                runner.run(test_app)
                
                # Should suggest Gradio, Streamlit, and Server
                calls = [str(call) for call in mock_print.call_args_list]
                all_calls = ' '.join(calls)
                
                assert 'gradio' in all_calls.lower()
                assert 'streamlit' in all_calls.lower()
                assert 'server' in all_calls.lower()
    
    def test_nicegui_explanation_provided(self, test_app):
        """Test NiceGUI runner explains why it's disabled."""
        runner = NiceGUI()
        
        with patch('yaapp.plugins.runners.nicegui.plugin.HAS_NICEGUI', True):
            with patch('builtins.print') as mock_print:
                runner.run(test_app)
                
                # Should explain the __name__ == '__main__' issue
                calls = [str(call) for call in mock_print.call_args_list]
                all_calls = ' '.join(calls)
                
                assert '__main__' in all_calls or 'plugin system' in all_calls
    
    def test_nicegui_returns_early(self, test_app):
        """Test NiceGUI runner returns early without starting server."""
        runner = NiceGUI()
        
        with patch('yaapp.plugins.runners.nicegui.plugin.HAS_NICEGUI', True):
            with patch('builtins.print'):
                # Should return None (early return)
                result = runner.run(test_app)
                assert result is None
    
    def test_nicegui_default_config_values(self):
        """Test NiceGUI runner default configuration values."""
        runner = NiceGUI()
        
        # Test default host
        assert runner.config.get('host', 'localhost') == 'localhost'
        
        # Test default port
        assert runner.config.get('port', 8080) == 8080
    
    def test_nicegui_config_override(self):
        """Test NiceGUI runner configuration override."""
        config = {'host': '0.0.0.0', 'port': 9999}
        runner = NiceGUI(config)
        
        assert runner.config['host'] == '0.0.0.0'
        assert runner.config['port'] == 9999
    
    @pytest.mark.asyncio
    async def test_nicegui_function_execution_helper(self, test_app):
        """Test NiceGUI function execution helper (even though disabled)."""
        # Test the helper function that would be used if NiceGUI worked
        from yaapp.plugins.runners.nicegui.plugin import _call_function_async
        
        with patch('yaapp.plugins.runners.nicegui.plugin.yaapp._registry', test_app._registry):
            # Test simple function
            result = await _call_function_async("add", {"x": 5, "y": 10})
            assert result == 15
            
            # Test function with error
            result = await _call_function_async("nonexistent", {})
            assert "error" in result
            assert "not found" in result["error"]
    
    def test_nicegui_legacy_setup_function_exists(self):
        """Test that legacy setup function still exists."""
        from yaapp.plugins.runners.nicegui.plugin import _setup_nicegui_interface
        
        # Should exist but not be used
        assert callable(_setup_nicegui_interface)
    
    def test_nicegui_clear_error_message(self, test_app):
        """Test NiceGUI provides clear error message."""
        runner = NiceGUI()
        
        with patch('yaapp.plugins.runners.nicegui.plugin.HAS_NICEGUI', True):
            with patch('builtins.print') as mock_print:
                runner.run(test_app)
                
                # Should have clear, helpful error message
                calls = [call.args[0] if call.args else '' for call in mock_print.call_args_list]
                
                # Should mention it's disabled
                assert any('Disabled' in call for call in calls)
                
                # Should be helpful, not just an error
                assert any('alternatives' in call.lower() or 'instead' in call.lower() for call in calls)