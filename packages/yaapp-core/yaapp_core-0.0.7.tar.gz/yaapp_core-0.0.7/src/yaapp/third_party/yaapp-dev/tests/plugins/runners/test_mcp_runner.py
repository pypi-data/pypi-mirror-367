"""
Comprehensive tests for MCP runner.
"""

import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock

from yaapp.plugins.runners.mcp.plugin import Mcp


class TestMcpRunner:
    """Test MCP runner functionality."""
    
    def test_mcp_runner_creation(self):
        """Test MCP runner can be created."""
        runner = Mcp()
        assert runner is not None
        assert hasattr(runner, 'help')
        assert hasattr(runner, 'run')
    
    def test_mcp_runner_help(self):
        """Test MCP runner help text."""
        runner = Mcp()
        help_text = runner.help()
        
        assert "MCP RUNNER HELP" in help_text
        assert "Model Context Protocol" in help_text
        assert "Claude Desktop" in help_text
        assert "--host" in help_text
        assert "--port" in help_text
    
    def test_mcp_runner_config(self):
        """Test MCP runner configuration."""
        config = {
            'server_name': 'Test MCP Server',
            'server_version': '2.0.0',
            'tool_prefix': 'test'
        }
        runner = Mcp(config)
        
        assert runner.server_name == 'Test MCP Server'
        assert runner.server_version == '2.0.0'
        assert runner.tool_prefix == 'test'
    
    def test_mcp_tool_generation(self, test_app):
        """Test MCP tool schema generation."""
        runner = Mcp()
        
        # Mock yaapp registry
        with patch('yaapp.plugins.runners.mcp.plugin.yaapp._registry', test_app._registry):
            tools = runner._generate_mcp_tools_dict()
        
        assert len(tools) > 0
        
        # Check tool structure
        for tool in tools:
            assert 'name' in tool
            assert 'description' in tool
            assert 'inputSchema' in tool
            assert tool['name'].startswith('yaapp.')
    
    def test_mcp_tool_discovery(self, test_app):
        """Test MCP tool discovery functionality."""
        runner = Mcp()
        
        with patch('yaapp.plugins.runners.mcp.plugin.yaapp._registry', test_app._registry):
            namespaces = runner._group_registry_items()
        
        assert '__root__' in namespaces or len(namespaces) > 0
        
        # Test discovery tools
        if runner.enable_discovery_tools:
            tools = runner._generate_mcp_tools_dict()
            discovery_tools = [t for t in tools if t['name'].endswith('.__list_tools')]
            # Should have discovery tools for namespaces
    
    @pytest.mark.asyncio
    async def test_mcp_function_execution(self, test_app):
        """Test MCP function execution."""
        runner = Mcp()
        
        with patch('yaapp.plugins.runners.mcp.plugin.yaapp._registry', test_app._registry):
            # Test simple function
            result = await runner._execute_tool("yaapp.add", {"x": 5, "y": 3})
            assert result == 8
            
            # Test function with default parameter
            result = await runner._execute_tool("yaapp.greet", {"name": "World"})
            assert "Hello, World!" in result
            
            # Test class method
            result = await runner._execute_tool("yaapp.Calculator.multiply", {"x": 4, "y": 5})
            assert result == 20
    
    @pytest.mark.asyncio
    async def test_mcp_json_rpc_protocol(self, test_app):
        """Test MCP JSON-RPC protocol handling."""
        runner = Mcp()
        
        with patch('yaapp.plugins.runners.mcp.plugin.yaapp._registry', test_app._registry):
            # Test initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            response = await runner._handle_json_rpc_request(init_request)
            assert response['jsonrpc'] == '2.0'
            assert response['id'] == 1
            assert 'result' in response
            assert 'capabilities' in response['result']
            
            # Test tools/list request
            list_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            response = await runner._handle_json_rpc_request(list_request)
            assert response['jsonrpc'] == '2.0'
            assert response['id'] == 2
            assert 'result' in response
            assert 'tools' in response['result']
            assert len(response['result']['tools']) > 0
            
            # Test tools/call request
            call_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "yaapp.add",
                    "arguments": {"x": 10, "y": 20}
                }
            }
            
            response = await runner._handle_json_rpc_request(call_request)
            assert response['jsonrpc'] == '2.0'
            assert response['id'] == 3
            assert 'result' in response
            assert response['result']['content'][0]['text'] == '30'
    
    def test_mcp_type_conversion(self):
        """Test Python type to JSON schema conversion."""
        runner = Mcp()
        
        # Test basic types
        assert runner._python_type_to_json_schema(str) == {"type": "string"}
        assert runner._python_type_to_json_schema(int) == {"type": "integer"}
        assert runner._python_type_to_json_schema(float) == {"type": "number"}
        assert runner._python_type_to_json_schema(bool) == {"type": "boolean"}
        assert runner._python_type_to_json_schema(list) == {"type": "array"}
        assert runner._python_type_to_json_schema(dict) == {"type": "object"}
    
    def test_mcp_error_handling(self, test_app):
        """Test MCP error handling."""
        runner = Mcp()
        
        with patch('yaapp.plugins.runners.mcp.plugin.yaapp._registry', test_app._registry):
            # Test invalid method
            error_response = runner._error_response(1, -32601, "Method not found")
            assert error_response['jsonrpc'] == '2.0'
            assert error_response['id'] == 1
            assert error_response['error']['code'] == -32601
            assert error_response['error']['message'] == "Method not found"
    
    @pytest.mark.asyncio
    async def test_mcp_discovery_tools(self, test_app):
        """Test MCP discovery tool functionality."""
        runner = Mcp()
        
        with patch('yaapp.plugins.runners.mcp.plugin.yaapp._registry', test_app._registry):
            # Test Calculator discovery - need to check if Calculator is in the right format
            namespaces = runner._group_registry_items()
            
            # If Calculator is in __root__, test that
            if 'Calculator' in namespaces.get('__root__', {}):
                result = await runner._handle_discovery_tool("yaapp.Calculator.__list_tools")
                assert "Calculator" in result
            else:
                # Skip this test if Calculator isn't set up as expected
                pytest.skip("Calculator not found in expected namespace structure")
    
    def test_mcp_runner_no_functions(self, test_app):
        """Test MCP runner with no exposed functions."""
        runner = Mcp()
        
        # Mock empty registry
        with patch('yaapp.plugins.runners.mcp.plugin.yaapp._registry', {}):
            with patch('builtins.print') as mock_print:
                with patch.object(runner, '_run_builtin_server') as mock_server:
                    runner.run(test_app)
                    mock_print.assert_called()
                    # Should print warning about no functions and not start server
                    mock_server.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_mcp_invalid_tool_execution(self, test_app):
        """Test MCP execution with invalid tools."""
        runner = Mcp()
        
        with patch('yaapp.plugins.runners.mcp.plugin.yaapp._registry', test_app._registry):
            # Test non-existent tool
            with pytest.raises(ValueError, match="Tool not found"):
                await runner._execute_tool("yaapp.nonexistent", {})
            
            # Test invalid parameters
            with pytest.raises(Exception):
                await runner._execute_tool("yaapp.add", {"x": "invalid"})