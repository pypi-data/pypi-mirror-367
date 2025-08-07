"""
Tests for API plugin execution to catch runtime bugs.
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from yaapp.plugins.api.plugin import Api, OpenAPIExecutor
from yaapp.result import Result, Ok, Err


class TestAPIPluginExecution:
    """Test API plugin execution functionality."""
    
    def test_execute_call_with_real_discoverer(self):
        """Test execute_call with a real discoverer to catch attribute errors."""
        config = {
            'type': 'openapi',
            'spec_url': 'https://example.com/api.yaml',
            'base_url': 'http://localhost:8000',
            'transport': 'http'
        }
        
        api = Api(config)
        api._load_config()
        
        # Set up discovered methods manually (simulating successful discovery)
        api._discovered_methods = {
            'auth': {
                'path': '/auth',
                'method': 'GET',
                'parameters': []
            }
        }
        
        # Create a real discoverer (this is where the bug occurs)
        from yaapp.plugins.api.plugin import OpenAPIDiscoverer
        api.discoverer = OpenAPIDiscoverer(config)
        
        # Create executor with the real discoverer
        api.executor = OpenAPIExecutor(config, api.discoverer, api)
        
        # Mock the HTTP request to avoid actual network calls
        with patch('requests.request') as mock_request:
            mock_response = Mock()
            mock_response.headers = {'content-type': 'application/json'}
            mock_response.json.return_value = {'status': 'ok'}
            mock_response.raise_for_status.return_value = None
            mock_request.return_value = mock_response
            
            # This should work without AttributeError
            result = api.execute_call('auth')
            
            assert result.is_ok(), f"Expected success but got error: {result.as_error if result.is_err() else 'N/A'}"
            assert result.unwrap() == {'status': 'ok'}
    
    def test_execute_call_nonexistent_method(self):
        """Test execute_call with nonexistent method."""
        api = Api({'type': 'openapi', 'base_url': 'http://localhost:8000'})
        api._load_config()
        api._discovered_methods = {}
        
        result = api.execute_call('nonexistent')
        
        assert result.is_err()
        assert "Method 'nonexistent' not found" in result.as_error
    
    def test_executor_accesses_correct_discovered_methods(self):
        """Test that executor accesses discovered methods from the right place."""
        config = {
            'type': 'openapi',
            'spec_url': 'https://example.com/api.yaml',
            'base_url': 'http://localhost:8000'
        }
        
        # Create API plugin with discovered methods
        api = Api(config)
        api._load_config()
        api._discovered_methods = {
            'test_method': {
                'path': '/test',
                'method': 'GET',
                'parameters': []
            }
        }
        
        # Create discoverer and executor
        from yaapp.plugins.api.plugin import OpenAPIDiscoverer
        api.discoverer = OpenAPIDiscoverer(config)
        api.executor = OpenAPIExecutor(config, api.discoverer, api)
        
        # The executor should be able to access the method info
        # This tests the fix for the AttributeError
        method_info = api._discovered_methods['test_method']
        
        # Mock the HTTP request
        with patch('requests.request') as mock_request:
            mock_response = Mock()
            mock_response.headers = {'content-type': 'application/json'}
            mock_response.json.return_value = {'result': 'success'}
            mock_response.raise_for_status.return_value = None
            mock_request.return_value = mock_response
            
            # This should work - the executor should get method info from api._discovered_methods
            result = api.execute_call('test_method')
            
            assert result.is_ok()
            assert result.unwrap() == {'result': 'success'}
    
    def test_executor_build_url_with_path_params(self):
        """Test URL building with path parameters."""
        config = {'base_url': 'http://localhost:8000'}
        executor = OpenAPIExecutor(config, Mock(), Mock())
        
        url = executor._build_url('/containers/{id}/start', {'id': 'abc123', 'other': 'value'})
        assert url == 'http://localhost:8000/containers/abc123/start'
    
    def test_executor_categorize_params_comprehensive(self):
        """Test parameter categorization with various parameter types."""
        config = {'base_url': 'http://localhost:8000'}
        executor = OpenAPIExecutor(config, Mock(), Mock())
        
        method_info = {
            'parameters': [
                {'name': 'id', 'in': 'path'},
                {'name': 'all', 'in': 'query'},
                {'name': 'filters', 'in': 'query'},
                {'name': 'body_data', 'in': 'body'}
            ]
        }
        
        kwargs = {
            'id': 'container123',
            'all': True,
            'filters': '{"status":["running"]}',
            'body_data': {'key': 'value'},
            'unknown_param': 'test'
        }
        
        path_params, query_params, body_params = executor._categorize_params(method_info, kwargs)
        
        assert path_params == {'id': 'container123'}
        assert query_params == {'all': True, 'filters': '{"status":["running"]}', 'unknown_param': 'test'}
        assert body_params == {'body_data': {'key': 'value'}}
    
    @patch('yaapp.plugins.api.plugin.requests.request')
    def test_executor_http_request_with_params(self, mock_request):
        """Test HTTP request with various parameter types."""
        config = {
            'base_url': 'http://localhost:8000',
            'transport': 'http',
            'spec_url': 'https://example.com/api.yaml'
        }
        
        api = Api(config)
        api._load_config()
        api._discovered_methods = {
            'containers_list': {
                'path': '/containers/json',
                'method': 'GET',
                'parameters': [
                    {'name': 'all', 'in': 'query'},
                    {'name': 'filters', 'in': 'query'}
                ]
            }
        }
        
        from yaapp.plugins.api.plugin import OpenAPIDiscoverer
        api.discoverer = OpenAPIDiscoverer(config)
        api.executor = OpenAPIExecutor(config, api.discoverer, api)
        
        mock_response = Mock()
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = [{'Id': 'abc123'}]
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Execute with query parameters
        result = api.execute_call('containers_list', all=True, filters='{"status":["running"]}')
        
        assert result.is_ok()
        assert result.unwrap() == [{'Id': 'abc123'}]
        
        # Verify the HTTP request was made correctly
        mock_request.assert_called_once_with(
            'GET',
            'http://localhost:8000/containers/json',
            params={'all': True, 'filters': '{"status":["running"]}'},
            json=None
        )
    
    def test_executor_http_transport(self):
        """Test HTTP transport configuration."""
        config = {
            'base_url': 'http://localhost:8000',
            'transport': 'http',
            'spec_url': 'https://example.com/api.yaml'
        }
        
        api = Api(config)
        api._load_config()
        api._discovered_methods = {
            'version': {
                'path': '/version',
                'method': 'GET',
                'parameters': []
            }
        }
        
        from yaapp.plugins.api.plugin import OpenAPIDiscoverer
        api.discoverer = OpenAPIDiscoverer(config)
        api.executor = OpenAPIExecutor(config, api.discoverer, api)
        
        # Mock regular HTTP request
        with patch('requests.request') as mock_request:
            mock_response = Mock()
            mock_response.headers = {'content-type': 'application/json'}
            mock_response.json.return_value = {'Version': '20.10.0'}
            mock_response.raise_for_status.return_value = None
            mock_request.return_value = mock_response
            
            result = api.execute_call('version')
            
            assert result.is_ok()
            assert result.unwrap() == {'Version': '20.10.0'}
            
            # Verify HTTP request was made
            mock_request.assert_called_once_with('GET', 'http://localhost:8000/version', params={}, json=None)
    
    def test_api_plugin_full_workflow(self):
        """Test the complete API plugin workflow from config to execution."""
        config = {
            'type': 'openapi',
            'spec_url': 'https://example.com/api.yaml',
            'base_url': 'http://localhost:8000',
            'transport': 'http'
        }
        
        # Mock the OpenAPI spec fetch
        mock_spec = {
            'swagger': '2.0',
            'paths': {
                '/health': {
                    'get': {
                        'operationId': 'HealthCheck',
                        'summary': 'Health check',
                        'parameters': []
                    }
                }
            }
        }
        
        with patch('requests.get') as mock_get, \
             patch('yaml.safe_load') as mock_yaml, \
             patch('requests.request') as mock_request:
            
            # Mock spec fetch
            mock_response = Mock()
            mock_response.text = 'mock yaml'
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            mock_yaml.return_value = mock_spec
            
            # Mock API execution
            mock_exec_response = Mock()
            mock_exec_response.headers = {'content-type': 'application/json'}
            mock_exec_response.json.return_value = {'status': 'healthy'}
            mock_exec_response.raise_for_status.return_value = None
            mock_request.return_value = mock_exec_response
            
            # Create and test API plugin
            api = Api(config)
            exposer = Mock()
            
            # This should discover endpoints
            api.expose_to_registry('api', exposer)
            
            # Verify discovery worked
            assert len(api._discovered_methods) > 0
            assert 'health' in api._discovered_methods
            
            # Execute discovered endpoint
            result = api.execute_call('health')
            
            assert result.is_ok()
            assert result.unwrap() == {'status': 'healthy'}
    
    def test_error_handling_in_execution(self):
        """Test error handling during API execution."""
        config = {
            'type': 'openapi',
            'spec_url': 'https://example.com/api.yaml',
            'base_url': 'http://localhost:8000'
        }
        
        api = Api(config)
        api._load_config()
        api._discovered_methods = {
            'failing_endpoint': {
                'path': '/fail',
                'method': 'GET',
                'parameters': []
            }
        }
        
        from yaapp.plugins.api.plugin import OpenAPIDiscoverer
        api.discoverer = OpenAPIDiscoverer(config)
        api.executor = OpenAPIExecutor(config, api.discoverer, api)
        
        # Mock a failing HTTP request
        with patch('requests.request') as mock_request:
            mock_request.side_effect = Exception("Connection failed")
            
            result = api.execute_call('failing_endpoint')
            
            assert result.is_err()
            assert "Connection failed" in result.as_error


class TestOpenAPIExecutorBugFixes:
    """Test specific bug fixes in OpenAPIExecutor."""
    
    def test_executor_does_not_access_discoverer_discovered_methods(self):
        """Test that executor doesn't try to access discoverer._discovered_methods."""
        config = {'base_url': 'http://localhost:8000'}
        
        # Create a discoverer without _discovered_methods attribute
        discoverer = Mock()
        # Explicitly ensure it doesn't have _discovered_methods
        if hasattr(discoverer, '_discovered_methods'):
            delattr(discoverer, '_discovered_methods')
        
        executor = OpenAPIExecutor(config, discoverer, Mock())
        
        # This should not try to access discoverer._discovered_methods
        # The method info should come from the API plugin's _discovered_methods
        method_info = {
            'path': '/test',
            'method': 'GET',
            'parameters': []
        }
        
        # Test URL building (should not access discoverer._discovered_methods)
        url = executor._build_url(method_info['path'], {})
        assert url == 'http://localhost:8000/test'
        
        # Test parameter categorization (should not access discoverer._discovered_methods)
        path_params, query_params, body_params = executor._categorize_params(method_info, {})
        assert path_params == {}
        assert query_params == {}
        assert body_params == {}


if __name__ == "__main__":
    # Run specific tests to verify the bug fix
    test_instance = TestAPIPluginExecution()
    
    print("🧪 Testing API Plugin Execution")
    print("=" * 40)
    
    try:
        print("1. Testing execute_call with real discoverer...")
        test_instance.test_execute_call_with_real_discoverer()
        print("✅ PASS")
        
        print("2. Testing executor accesses correct discovered methods...")
        test_instance.test_executor_accesses_correct_discovered_methods()
        print("✅ PASS")
        
        print("3. Testing full workflow...")
        test_instance.test_api_plugin_full_workflow()
        print("✅ PASS")
        
        print("4. Testing error handling...")
        test_instance.test_error_handling_in_execution()
        print("✅ PASS")
        
        print("\n🎉 All execution tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise