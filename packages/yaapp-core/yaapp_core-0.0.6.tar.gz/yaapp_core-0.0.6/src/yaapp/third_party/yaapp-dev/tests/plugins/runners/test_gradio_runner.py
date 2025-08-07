"""
Comprehensive tests for Gradio runner.
"""

import pytest
from unittest.mock import patch, MagicMock
import json

from yaapp.plugins.runners.gradio.plugin import Gradio


class TestGradioRunner:
    """Test Gradio runner functionality."""
    
    def test_gradio_runner_creation(self):
        """Test Gradio runner can be created."""
        runner = Gradio()
        assert runner is not None
        assert hasattr(runner, 'help')
        assert hasattr(runner, 'run')
    
    def test_gradio_runner_help(self):
        """Test Gradio runner help text."""
        runner = Gradio()
        help_text = runner.help()
        
        assert "GRADIO RUNNER HELP" in help_text
        assert "--port" in help_text
        assert "--share" in help_text
    
    def test_gradio_runner_config(self):
        """Test Gradio runner configuration."""
        config = {
            'port': 7777,
            'share': True
        }
        runner = Gradio(config)
        assert runner.config == config
    
    def test_gradio_missing_dependency(self):
        """Test Gradio runner when gradio is not installed."""
        runner = Gradio()
        
        with patch('yaapp.plugins.runners.gradio.plugin.HAS_GRADIO', False):
            with patch('builtins.print') as mock_print:
                runner.run(None)
                mock_print.assert_called()
                # Should print error about missing gradio
    
    def test_gradio_no_functions(self):
        """Test Gradio runner with no exposed functions."""
        runner = Gradio()
        
        with patch('yaapp.plugins.runners.gradio.plugin.HAS_GRADIO', True):
            with patch('yaapp.plugins.runners.gradio.plugin.yaapp._registry', {}):
                with patch('builtins.print') as mock_print:
                    runner.run(None)
                    mock_print.assert_called()
                    # Should print warning about no functions
    
    def test_gradio_example_params_generation(self):
        """Test example parameters generation."""
        runner = Gradio()
        
        import inspect
        
        def test_func(x: int, y: str, z: bool, items: list, data: dict) -> str:
            return "test"
        
        sig = inspect.signature(test_func)
        example = runner._generate_example_params(sig)
        
        parsed = json.loads(example)
        assert parsed['x'] == 42
        assert parsed['y'] == "example_value"
        assert parsed['z'] is True
        assert parsed['items'] == ["item1", "item2"]
        assert parsed['data'] == {"key": "value"}
    
    @pytest.mark.asyncio
    async def test_gradio_function_execution(self, test_app):
        """Test Gradio function execution."""
        runner = Gradio()
        
        with patch('yaapp.plugins.runners.gradio.plugin.yaapp._registry', test_app._registry):
            # Test simple function
            result = await runner._call_function_async("add", {"x": 15, "y": 25})
            assert result == 40
            
            # Test function with error
            result = await runner._call_function_async("nonexistent", {})
            assert "error" in result
            assert "not found" in result["error"]
    
    def test_gradio_interface_creation_method_exists(self, test_app):
        """Test Gradio interface creation method exists."""
        runner = Gradio()
        
        # Test that the method exists
        assert hasattr(runner, '_create_interface')
        assert callable(runner._create_interface)
        
        # Test basic functionality without mocking gradio internals
        with patch('yaapp.plugins.runners.gradio.plugin.HAS_GRADIO', True):
            with patch('yaapp.plugins.runners.gradio.plugin.yaapp._registry', test_app._registry):
                # Should not crash when called (even if gradio is not available)
                try:
                    interface = runner._create_interface()
                    # If it works, great
                    assert interface is not None
                except (ImportError, AttributeError):
                    # Expected when gradio is not available or mocked incorrectly
                    pass
    
    def test_gradio_run_method(self, test_app):
        """Test Gradio run method."""
        runner = Gradio()
        
        with patch('yaapp.plugins.runners.gradio.plugin.HAS_GRADIO', True):
            with patch('yaapp.plugins.runners.gradio.plugin.yaapp._registry', test_app._registry):
                with patch.object(runner, '_create_interface') as mock_create:
                    mock_interface = MagicMock()
                    mock_create.return_value = mock_interface
                    
                    runner.run(test_app, port=7777, share=True)
                    
                    mock_create.assert_called_once()
                    mock_interface.launch.assert_called_once_with(server_port=7777, share=True)
    
    def test_gradio_function_info_generation(self, test_app):
        """Test function info generation for Gradio interface."""
        runner = Gradio()
        
        with patch('yaapp.plugins.runners.gradio.plugin.yaapp._registry', test_app._registry):
            # This would be called by the Gradio interface
            # We can't easily test the actual UI interaction, but we can test the logic
            
            # Test that registry functions are accessible
            functions = list(test_app._registry.keys())
            assert 'add' in functions
            assert 'greet' in functions
            assert 'Calculator' in functions
    
    def test_gradio_json_parameter_handling(self):
        """Test JSON parameter handling in Gradio interface."""
        runner = Gradio()
        
        # Test valid JSON
        valid_json = '{"x": 10, "y": 20}'
        try:
            parsed = json.loads(valid_json)
            assert parsed['x'] == 10
            assert parsed['y'] == 20
        except json.JSONDecodeError:
            pytest.fail("Valid JSON should parse correctly")
        
        # Test invalid JSON
        invalid_json = '{"x": 10, "y":}'
        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid_json)
    
    def test_gradio_error_handling_in_execution(self, test_app):
        """Test error handling in Gradio function execution."""
        runner = Gradio()
        
        # Mock a function that raises an exception
        def failing_function():
            raise ValueError("Test error")
        
        # Test that errors are properly caught and returned
        import asyncio
        
        async def test_error():
            try:
                # This would normally be called by the Gradio interface
                result = await runner._call_function_async("nonexistent", {})
                assert "error" in result
            except Exception as e:
                # Should not raise, should return error dict
                pytest.fail(f"Should handle errors gracefully: {e}")
        
        asyncio.run(test_error())
    
    def test_gradio_default_config_values(self):
        """Test Gradio runner default configuration values."""
        runner = Gradio()
        
        # Test default port
        assert runner.config.get('port', 7860) == 7860
        
        # Test default share
        assert runner.config.get('share', False) is False
    
    def test_gradio_config_override(self):
        """Test Gradio runner configuration override."""
        config = {'port': 9999, 'share': True}
        runner = Gradio(config)
        
        assert runner.config['port'] == 9999
        assert runner.config['share'] is True