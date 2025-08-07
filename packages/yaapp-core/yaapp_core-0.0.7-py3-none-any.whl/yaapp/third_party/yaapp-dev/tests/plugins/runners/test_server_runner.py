"""
Comprehensive tests for Server runner.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

from yaapp.plugins.runners.server.plugin import ServerRunner as Server


class TestServerRunner:
    """Test Server runner functionality."""
    
    def test_server_runner_creation(self):
        """Test Server runner can be created."""
        runner = Server()
        assert runner is not None
        assert hasattr(runner, 'help')
        assert hasattr(runner, 'run')
    
    def test_server_runner_help(self):
        """Test Server runner help text."""
        runner = Server()
        help_text = runner.help()
        
        assert "SERVER RUNNER HELP" in help_text
        assert "--host" in help_text
        assert "--port" in help_text
        assert "--reload" in help_text
        assert "--workers" in help_text
    
    def test_server_runner_config(self):
        """Test Server runner configuration."""
        config = {
            'host': '0.0.0.0',
            'port': 9000,
            'reload': True,
            'workers': 4
        }
        runner = Server(config)
        assert runner.config == config
    
    def test_server_command_tree_building(self, test_app):
        """Test command tree building."""
        runner = Server()
        
        with patch('yaapp.plugins.runners.server.plugin.yaapp._registry', test_app._registry):
            tree = runner._build_command_tree()
        
        assert isinstance(tree, dict)
        
        # Should have functions and classes
        assert 'add' in tree
        assert 'greet' in tree
        assert 'Calculator' in tree
        
        # Check function structure
        assert tree['add']['type'] == 'function'
        assert 'func' in tree['add']
        
        # Check class structure
        assert tree['Calculator']['type'] == 'namespace'
        assert 'children' in tree['Calculator']
        assert 'multiply' in tree['Calculator']['children']
    
    def test_server_rpc_tree_building(self, test_app):
        """Test RPC tree building."""
        runner = Server()
        
        with patch('yaapp.plugins.runners.server.plugin.yaapp._registry', test_app._registry):
            tree = runner._build_rpc_tree()
        
        assert isinstance(tree, dict)
        
        # Should have functions with signatures
        for name, item in tree.items():
            if item['type'] == 'function':
                assert 'signature' in item
                assert 'description' in item
            elif item['type'] == 'class':
                assert 'methods' in item
    
    def test_server_function_signature_extraction(self):
        """Test function signature extraction."""
        runner = Server()
        
        def test_func(x: int, y: str = "default") -> str:
            return f"{x}: {y}"
        
        signature = runner._get_function_signature(test_func)
        
        assert 'x' in signature
        assert 'y' in signature
        assert signature['x'] == 'int'
        assert 'default' in signature['y']
    
    @pytest.mark.asyncio
    async def test_server_function_execution(self, test_app):
        """Test server function execution."""
        runner = Server()
        
        with patch('yaapp.plugins.runners.server.plugin.yaapp._registry', test_app._registry):
            # Test simple function
            result = await runner._call_function_async("add", {"x": 7, "y": 3})
            assert result == 10
            
            # Test function with default parameter
            result = await runner._call_function_async("greet", {"name": "Test"})
            assert "Hello, Test!" in result
    
    @pytest.mark.asyncio
    async def test_server_method_execution(self, test_app):
        """Test server method execution."""
        runner = Server()
        
        with patch('yaapp.plugins.runners.server.plugin.yaapp._registry', test_app._registry):
            # Create a mock method
            def mock_method(x, y):
                return x * y
            
            result = await runner._call_function_async_method(mock_method, {"x": 6, "y": 7})
            assert result == 42
    
    def test_server_no_functions(self):
        """Test server with no exposed functions."""
        runner = Server()
        
        with patch('yaapp.plugins.runners.server.plugin.yaapp._registry', {}):
            with patch('builtins.print') as mock_print:
                runner._start_server('localhost', 8000, False, 1)
                mock_print.assert_called()
                # Should print warning about no functions
    
    def test_server_missing_dependencies(self, test_app):
        """Test server behavior when FastAPI is missing."""
        runner = Server()
        
        with patch('yaapp.plugins.runners.server.plugin.yaapp._registry', test_app._registry):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'fastapi'")):
                with patch('builtins.print') as mock_print:
                    runner._start_server('localhost', 8000, False, 1)
                    mock_print.assert_called()
                    # Should print error about missing dependencies
    
    @pytest.mark.asyncio
    async def test_server_error_handling(self, test_app):
        """Test server error handling."""
        runner = Server()
        
        with patch('yaapp.plugins.runners.server.plugin.yaapp._registry', test_app._registry):
            # Test non-existent function
            result = await runner._call_function_async("nonexistent", {})
            assert "error" in result
            assert "not found" in result["error"]
            
            # Test function that raises exception
            with patch.object(test_app._registry['Calculator'][1], 'run_async', 
                            side_effect=Exception("Test error")):
                result = await runner._call_function_async("Calculator", {})
                assert "error" in result
    
    def test_server_run_method(self, test_app):
        """Test server run method."""
        runner = Server()
        
        with patch('yaapp.plugins.runners.server.plugin.yaapp._registry', test_app._registry):
            with patch.object(runner, '_start_server') as mock_start:
                runner.run(test_app, host='test-host', port=9999, reload=True, workers=2)
                
                mock_start.assert_called_once_with('test-host', 9999, True, 2)
    
    def test_server_class_methods_extraction(self, test_app):
        """Test class methods extraction."""
        runner = Server()
        
        # Get Calculator class from registry
        calc_class = test_app._registry['Calculator'][0]
        methods = runner._get_class_methods(calc_class)
        
        assert 'multiply' in methods
        assert 'divide' in methods
        
        # Check method structure
        assert methods['multiply']['type'] == 'function'
        assert 'func' in methods['multiply']
        assert 'class' in methods['multiply']
    
    def test_server_streaming_endpoints_method_exists(self, test_app):
        """Test that streaming endpoints method exists."""
        runner = Server()
        
        # Test that the method exists
        assert hasattr(runner, '_add_streaming_endpoints')
        assert callable(runner._add_streaming_endpoints)
        
        # Test basic call without streaming utilities
        with patch('yaapp.plugins.runners.server.plugin.yaapp._registry', test_app._registry):
            tree = runner._build_command_tree()
            
            # Should not crash when streaming utilities are missing
            try:
                runner._add_streaming_endpoints(MagicMock(), tree)
            except ImportError:
                # Expected when streaming utilities are not available
                pass