#!/usr/bin/env python3
"""
Test AppProxy plugin async functionality.
"""

import pytest
import asyncio
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp.plugins.app_proxy.plugin import AppProxy


class TestAppProxyAsync:
    """Test AppProxy plugin async functionality."""
    
    @pytest.fixture
    def app_proxy_config(self):
        """Create test app proxy configuration."""
        return {
            'target_url': 'http://localhost:8001',
            'timeout': 30.0,
            'max_retries': 3
        }
    
    @pytest.fixture
    def app_proxy(self, app_proxy_config):
        """Create an AppProxy instance for testing."""
        return AppProxy(app_proxy_config)
    
    @pytest.fixture
    def mock_api_response(self):
        """Mock API discovery response."""
        return {
            'functions': {
                'greet': {
                    'type': 'function',
                    'parameters': [
                        {'name': 'name', 'type': 'string', 'required': True}
                    ]
                },
                'calculate': {
                    'type': 'function', 
                    'parameters': [
                        {'name': 'x', 'type': 'number', 'required': True},
                        {'name': 'y', 'type': 'number', 'required': True}
                    ]
                }
            }
        }
    
    def test_app_proxy_initialization_with_config(self, app_proxy_config):
        """Test AppProxy initialization with config."""
        proxy = AppProxy(app_proxy_config)
        
        assert proxy.target_url == 'http://localhost:8001'
        assert proxy.timeout == 30.0
        assert proxy.max_retries == 3
        assert proxy._discovered_functions == {}
        assert proxy._failure_count == 0
        assert proxy._circuit_open is False
    
    def test_app_proxy_initialization_with_target_url(self):
        """Test AppProxy initialization with direct target_url."""
        proxy = AppProxy(target_url='http://example.com:8080')
        
        assert proxy.target_url == 'http://example.com:8080'
        assert proxy.timeout == 30.0
        assert proxy.max_retries == 3
    
    def test_app_proxy_initialization_error(self):
        """Test AppProxy initialization error handling."""
        with pytest.raises(ValueError, match="Either config or target_url must be provided"):
            AppProxy()
    
    def test_circuit_breaker_functionality(self, app_proxy):
        """Test circuit breaker functionality."""
        # Initially circuit should be closed
        assert app_proxy._check_circuit_breaker() is True
        
        # Record failures to open circuit
        app_proxy._record_failure()
        app_proxy._record_failure()
        app_proxy._record_failure()
        
        # Circuit should now be open
        assert app_proxy._circuit_open is True
        assert app_proxy._check_circuit_breaker() is False
        
        # Record success to reset circuit
        app_proxy._record_success()
        assert app_proxy._circuit_open is False
        assert app_proxy._failure_count == 0
    
    @pytest.mark.asyncio
    async def test_get_session_creation(self, app_proxy):
        """Test HTTP session creation."""
        # Mock aiohttp availability
        with patch('yaapp.plugins.app_proxy.plugin.HAS_AIOHTTP', True):
            with patch('yaapp.plugins.app_proxy.plugin.aiohttp') as mock_aiohttp:
                mock_session = Mock()
                mock_aiohttp.ClientSession.return_value = mock_session
                mock_aiohttp.ClientTimeout.return_value = Mock()
                mock_aiohttp.TCPConnector.return_value = Mock()
                
                session = await app_proxy._get_session()
                
                assert session == mock_session
                mock_aiohttp.ClientSession.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_discover_remote_api_success(self, app_proxy, mock_api_response):
        """Test successful remote API discovery."""
        with patch('yaapp.plugins.app_proxy.plugin.HAS_AIOHTTP', True):
            with patch.object(app_proxy, '_discover_remote_api_async') as mock_discover:
                mock_discover.return_value = Mock()
                mock_discover.return_value.is_ok.return_value = True
                mock_discover.return_value.unwrap.return_value = mock_api_response['functions']
                
                result = await app_proxy._discover_remote_api()
                
                assert result.is_ok()
                functions = result.unwrap()
                assert 'greet' in functions
                assert 'calculate' in functions
    
    @pytest.mark.asyncio
    async def test_discover_remote_api_with_mock_session(self, app_proxy, mock_api_response):
        """Test API discovery with mocked HTTP session."""
        with patch('yaapp.plugins.app_proxy.plugin.HAS_AIOHTTP', True):
            # Mock session and response properly
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_api_response)
            
            # Create proper async context manager
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.get.return_value = mock_context
            
            with patch.object(app_proxy, '_get_session', return_value=mock_session):
                result = await app_proxy._discover_remote_api_async()
                
                assert result.is_ok()
                functions = result.unwrap()
                assert 'greet' in functions
                assert 'calculate' in functions
    
    @pytest.mark.asyncio
    async def test_discover_remote_api_http_error(self, app_proxy):
        """Test API discovery with HTTP error."""
        with patch('yaapp.plugins.app_proxy.plugin.HAS_AIOHTTP', True):
            # Mock session with error response
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 404
            mock_response.reason = "Not Found"
            
            # Create proper async context manager
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.get.return_value = mock_context
            
            with patch.object(app_proxy, '_get_session', return_value=mock_session):
                result = await app_proxy._discover_remote_api_async()
                
                assert result.is_err()
                assert "HTTP 404" in result.as_error
    
    @pytest.mark.asyncio
    async def test_discover_remote_api_timeout(self, app_proxy):
        """Test API discovery with timeout."""
        with patch('yaapp.plugins.app_proxy.plugin.HAS_AIOHTTP', True):
            with patch.object(app_proxy, '_get_session') as mock_get_session:
                mock_get_session.side_effect = asyncio.TimeoutError()
                
                result = await app_proxy._discover_remote_api_async()
                
                assert result.is_err()
                assert "timeout" in result.as_error.lower()
    
    @pytest.mark.asyncio
    async def test_make_rpc_call_success(self, app_proxy):
        """Test successful RPC call."""
        with patch('yaapp.plugins.app_proxy.plugin.HAS_AIOHTTP', True):
            # Mock session and response
            mock_session = Mock()
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"result": "Hello, World!"})
            
            # Create proper async context manager
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_response)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_session.post.return_value = mock_context
            
            with patch.object(app_proxy, '_get_session', return_value=mock_session):
                result = await app_proxy._make_rpc_call_async('greet', {'name': 'World'})
                
                assert result == {"result": "Hello, World!"}
    
    @pytest.mark.asyncio
    async def test_make_rpc_call_with_error_response(self, app_proxy):
        """Test RPC call with error response."""
        with patch('yaapp.plugins.app_proxy.plugin.HAS_AIOHTTP', True):
            # Mock session with error response
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"error": "Function not found"}
            
            mock_session.post.return_value.__aenter__.return_value = mock_response
            
            with patch.object(app_proxy, '_get_session', return_value=mock_session):
                result = await app_proxy._make_rpc_call_async('nonexistent', {})
                
                assert result is None
    
    @pytest.mark.asyncio
    async def test_make_rpc_call_http_error(self, app_proxy):
        """Test RPC call with HTTP error."""
        with patch('yaapp.plugins.app_proxy.plugin.HAS_AIOHTTP', True):
            # Mock session with HTTP error
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text.return_value = "Internal Server Error"
            
            mock_session.post.return_value.__aenter__.return_value = mock_response
            
            with patch.object(app_proxy, '_get_session', return_value=mock_session):
                result = await app_proxy._make_rpc_call_async('greet', {'name': 'World'})
                
                assert result is None
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_during_rpc_call(self, app_proxy):
        """Test circuit breaker behavior during RPC calls."""
        # Open the circuit breaker
        app_proxy._circuit_open = True
        app_proxy._last_failure_time = 0  # Long time ago
        
        with patch('yaapp.plugins.app_proxy.plugin.HAS_AIOHTTP', True):
            result = await app_proxy._make_rpc_call_async('greet', {'name': 'World'})
            
            assert result is None
    
    def test_flatten_api_tree(self, app_proxy):
        """Test API tree flattening functionality."""
        tree = {
            'greet': {'type': 'function'},
            'math': {
                'commands': {
                    'add': {'type': 'function'},
                    'subtract': {'type': 'function'}
                }
            },
            'Calculator': {
                'methods': {
                    'multiply': {'type': 'function'},
                    'divide': {'type': 'function'}
                }
            }
        }
        
        flattened = app_proxy._flatten_api_tree(tree)
        
        assert 'greet' in flattened
        assert 'math.add' in flattened
        assert 'math.subtract' in flattened
        assert 'Calculator.multiply' in flattened
        assert 'Calculator.divide' in flattened
    
    def test_create_proxy_functions(self, app_proxy):
        """Test proxy function creation."""
        functions = {
            'greet': {
                'type': 'function',
                'parameters': [{'name': 'name', 'type': 'string', 'required': True}]
            }
        }
        
        app_proxy._create_proxy_functions(functions)
        
        assert 'greet' in app_proxy._proxy_functions
        assert callable(app_proxy._proxy_functions['greet'])
    
    def test_execute_call_function_not_found(self, app_proxy):
        """Test execute_call with function not found."""
        result = app_proxy.execute_call('nonexistent_function')
        
        assert result is None
    
    def test_execute_call_with_discovered_function(self, app_proxy):
        """Test execute_call with discovered function."""
        # Set up discovered functions
        app_proxy._discovered_functions = {
            'greet': {'type': 'function'}
        }
        
        # Mock the RPC call
        with patch.object(app_proxy, '_make_rpc_call') as mock_rpc:
            with patch('asyncio.run') as mock_run:
                mock_run.return_value = "Hello, World!"
                
                result = app_proxy.execute_call('greet', name='World')
                
                assert result == "Hello, World!"
    
    @pytest.mark.asyncio
    async def test_execute_call_async(self, app_proxy):
        """Test async version of execute_call."""
        # Set up discovered functions
        app_proxy._discovered_functions = {
            'greet': {'type': 'function'}
        }
        
        with patch.object(app_proxy, '_make_rpc_call') as mock_rpc:
            mock_rpc.return_value = "Hello, World!"
            
            result = await app_proxy.execute_call_async('greet', name='World')
            
            assert result == "Hello, World!"
    
    def test_get_available_functions(self, app_proxy):
        """Test getting available functions."""
        functions = {
            'greet': {'type': 'function'},
            'calculate': {'type': 'function'}
        }
        app_proxy._discovered_functions = functions
        
        available = app_proxy.get_available_functions()
        
        assert available == functions
        assert available is not app_proxy._discovered_functions  # Should be a copy
    
    @pytest.mark.asyncio
    async def test_context_manager(self, app_proxy):
        """Test AppProxy as async context manager."""
        async with app_proxy as proxy:
            assert proxy is app_proxy
        
        # close() should have been called
        # We can't easily test this without mocking the session
    
    def test_has_aiohttp_flag(self, app_proxy):
        """Test that HAS_AIOHTTP flag is properly set."""
        from yaapp.plugins.app_proxy.plugin import HAS_AIOHTTP
        # Should be a boolean
        assert isinstance(HAS_AIOHTTP, bool)
    
    def test_sync_fallback_methods_exist(self, app_proxy):
        """Test that sync fallback methods exist."""
        # Test that the fallback methods exist
        assert hasattr(app_proxy, '_discover_remote_api_sync')
        assert hasattr(app_proxy, '_make_rpc_call_sync')
        assert callable(app_proxy._discover_remote_api_sync)
        assert callable(app_proxy._make_rpc_call_sync)
    
    def test_expose_to_registry_error_handling(self, app_proxy):
        """Test expose_to_registry error handling."""
        with patch.object(app_proxy, '_async_expose_to_registry') as mock_async:
            mock_async.side_effect = Exception("Network error")
            
            with pytest.raises(ValueError, match="AppProxy exposure failed"):
                app_proxy.expose_to_registry('test', Mock())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])