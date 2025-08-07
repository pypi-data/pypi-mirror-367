"""
Comprehensive tests for Streamlit runner.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os

from yaapp.plugins.runners.streamlit.plugin import Streamlit


class TestStreamlitRunner:
    """Test Streamlit runner functionality."""
    
    def test_streamlit_runner_creation(self):
        """Test Streamlit runner can be created."""
        runner = Streamlit()
        assert runner is not None
        assert hasattr(runner, 'help')
        assert hasattr(runner, 'run')
    
    def test_streamlit_runner_help(self):
        """Test Streamlit runner help text."""
        runner = Streamlit()
        help_text = runner.help()
        
        assert "STREAMLIT RUNNER HELP" in help_text
        assert "--port" in help_text
    
    def test_streamlit_runner_config(self):
        """Test Streamlit runner configuration."""
        config = {'port': 8888}
        runner = Streamlit(config)
        assert runner.config == config
    
    def test_streamlit_missing_dependency(self):
        """Test Streamlit runner when streamlit is not installed."""
        runner = Streamlit()
        
        with patch('yaapp.plugins.runners.streamlit.plugin.HAS_STREAMLIT', False):
            with patch('builtins.print') as mock_print:
                runner.run(None)
                mock_print.assert_called()
                # Should print error about missing streamlit
    
    def test_streamlit_no_functions(self):
        """Test Streamlit runner with no exposed functions."""
        runner = Streamlit()
        
        with patch('yaapp.plugins.runners.streamlit.plugin.HAS_STREAMLIT', True):
            with patch('yaapp.plugins.runners.streamlit.plugin.yaapp._registry', {}):
                with patch('builtins.print') as mock_print:
                    runner.run(None)
                    mock_print.assert_called()
                    # Should print warning about no functions
    
    def test_streamlit_app_generation(self, test_app):
        """Test Streamlit app content generation."""
        runner = Streamlit()
        
        with patch('yaapp.plugins.runners.streamlit.plugin.yaapp._registry', test_app._registry):
            app_content = runner._generate_streamlit_app()
        
        assert isinstance(app_content, str)
        assert 'import streamlit as st' in app_content
        assert 'yaapp Streamlit Interface' in app_content
        assert 'FUNCTIONS_DATA' in app_content
        
        # Should contain function data
        assert 'add' in app_content
        assert 'greet' in app_content
        assert 'Calculator' in app_content
    
    def test_streamlit_function_data_extraction(self, test_app):
        """Test function data extraction for Streamlit app."""
        runner = Streamlit()
        
        with patch('yaapp.plugins.runners.streamlit.plugin.yaapp._registry', test_app._registry):
            app_content = runner._generate_streamlit_app()
        
        # Check that FUNCTIONS_DATA is present
        assert 'FUNCTIONS_DATA' in app_content
        
        # Check that function names are present
        assert 'add' in app_content
        assert 'greet' in app_content
        assert 'Calculator' in app_content
        
        # Check basic structure elements
        assert 'signature' in app_content
        assert 'doc' in app_content
        assert 'params' in app_content
    
    @pytest.mark.asyncio
    async def test_streamlit_function_execution(self, test_app):
        """Test Streamlit function execution."""
        runner = Streamlit()
        
        with patch('yaapp.plugins.runners.streamlit.plugin.yaapp._registry', test_app._registry):
            # Test simple function
            result = await runner._call_function_async("add", {"x": 12, "y": 8})
            assert result == 20
            
            # Test function with error
            result = await runner._call_function_async("nonexistent", {})
            assert "error" in result
            assert "not found" in result["error"]
    
    def test_streamlit_run_method(self, test_app):
        """Test Streamlit run method."""
        runner = Streamlit()
        
        with patch('yaapp.plugins.runners.streamlit.plugin.HAS_STREAMLIT', True):
            with patch('yaapp.plugins.runners.streamlit.plugin.yaapp._registry', test_app._registry):
                with patch('tempfile.NamedTemporaryFile') as mock_temp:
                    with patch('subprocess.run') as mock_subprocess:
                        with patch('os.unlink') as mock_unlink:
                            # Mock temporary file
                            mock_file = MagicMock()
                            mock_file.name = '/tmp/test_streamlit.py'
                            mock_temp.return_value.__enter__.return_value = mock_file
                            
                            runner.run(test_app, port=8888)
                            
                            # Should create temp file and run streamlit
                            mock_temp.assert_called_once()
                            mock_subprocess.assert_called_once()
                            mock_unlink.assert_called_once_with('/tmp/test_streamlit.py')
                            
                            # Check subprocess call
                            call_args = mock_subprocess.call_args[0][0]
                            assert 'streamlit' in call_args
                            assert 'run' in call_args
                            assert '--server.port' in call_args
                            assert '8888' in call_args
    
    def test_streamlit_parameter_type_handling(self, test_app):
        """Test parameter type handling in Streamlit app generation."""
        runner = Streamlit()
        
        # Add a function with various parameter types
        def complex_func(name: str, age: int, height: float, active: bool = True):
            return f"{name} is {age} years old"
        
        # Mock registry with complex function
        mock_registry = {
            'complex_func': (complex_func, MagicMock())
        }
        
        with patch('yaapp.plugins.runners.streamlit.plugin.yaapp._registry', mock_registry):
            app_content = runner._generate_streamlit_app()
        
        # Should handle different parameter types
        assert 'str' in app_content
        assert 'int' in app_content
        assert 'float' in app_content
        assert 'bool' in app_content
    
    def test_streamlit_error_handling_in_execution(self, test_app):
        """Test error handling in Streamlit function execution."""
        runner = Streamlit()
        
        import asyncio
        
        async def test_error():
            with patch('yaapp.plugins.runners.streamlit.plugin.yaapp._registry', test_app._registry):
                # Test non-existent function
                result = await runner._call_function_async("nonexistent", {})
                assert "error" in result
                assert "not found" in result["error"]
        
        asyncio.run(test_error())
    
    def test_streamlit_default_config_values(self):
        """Test Streamlit runner default configuration values."""
        runner = Streamlit()
        
        # Test default port
        assert runner.config.get('port', 8501) == 8501
    
    def test_streamlit_config_override(self):
        """Test Streamlit runner configuration override."""
        config = {'port': 9999}
        runner = Streamlit(config)
        
        assert runner.config['port'] == 9999
    
    def test_streamlit_app_structure(self, test_app):
        """Test generated Streamlit app structure."""
        runner = Streamlit()
        
        with patch('yaapp.plugins.runners.streamlit.plugin.yaapp._registry', test_app._registry):
            app_content = runner._generate_streamlit_app()
        
        # Should have proper Streamlit structure
        assert 'st.title(' in app_content
        assert 'st.sidebar' in app_content
        assert 'st.button(' in app_content
        assert 'st.json(' in app_content
        
        # Should handle function execution
        assert 'Execute Function' in app_content
        assert 'if st.button(' in app_content
    
    def test_streamlit_subprocess_command(self, test_app):
        """Test Streamlit subprocess command construction."""
        runner = Streamlit()
        
        with patch('yaapp.plugins.runners.streamlit.plugin.HAS_STREAMLIT', True):
            with patch('yaapp.plugins.runners.streamlit.plugin.yaapp._registry', test_app._registry):
                with patch('tempfile.NamedTemporaryFile') as mock_temp:
                    with patch('subprocess.run') as mock_subprocess:
                        with patch('os.unlink'):
                            mock_file = MagicMock()
                            mock_file.name = '/tmp/test.py'
                            mock_temp.return_value.__enter__.return_value = mock_file
                            
                            runner.run(test_app, port=8765)
                            
                            # Check the subprocess command
                            call_args = mock_subprocess.call_args[0][0]
                            expected_cmd = [
                                'streamlit', 'run', '/tmp/test.py',
                                '--server.port', '8765',
                                '--server.headless', 'true'
                            ]
                            assert call_args == expected_cmd