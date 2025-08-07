"""
Tests for the API plugin to verify it actually works.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from yaapp.plugins.api.plugin import Api, OpenAPIDiscoverer, OpenAPIExecutor


class TestApiPlugin:
    """Test the API plugin functionality."""
    
    def test_api_plugin_init_with_config(self):
        """Test that API plugin initializes with config."""
        config = {
            'type': 'openapi',
            'spec_url': 'https://example.com/api.yaml',
            'base_url': 'http://localhost:8000',
            'transport': 'http'
        }
        
        api = Api(config)
        assert api._provided_config == config
        assert api.config is None  # Not loaded yet
        assert api.discoverer is None
        assert api.executor is None
        assert api._discovered_methods == {}
    
    def test_api_plugin_init_without_config(self):
        """Test that API plugin initializes without config."""
        api = Api()
        assert api._provided_config is None
        assert api.config is None
        assert api.discoverer is None
        assert api.executor is None
        assert api._discovered_methods == {}
    
    def test_load_config_with_provided_config(self):
        """Test that _load_config uses provided config."""
        config = {
            'type': 'openapi',
            'spec_url': 'https://example.com/api.yaml'
        }
        
        api = Api(config)
        api._load_config()
        
        assert api.config == config
    
    def test_load_config_without_provided_config(self):
        """Test that _load_config falls back to yaapp config."""
        api = Api()
        
        # Mock yaapp instance with config
        with patch('yaapp.plugins.api.plugin.yaapp') as mock_yaapp:
            mock_config = Mock()
            mock_config.discovered_sections = {
                'api': {
                    'type': 'openapi',
                    'spec_url': 'https://example.com/api.yaml'
                }
            }
            mock_yaapp._config = mock_config
            
            api._load_config()
            
            assert api.config == {
                'type': 'openapi',
                'spec_url': 'https://example.com/api.yaml'
            }
    
    def test_load_config_no_yaapp_config(self):
        """Test that _load_config handles missing yaapp config."""
        api = Api()
        
        # Mock yaapp instance without config
        with patch('yaapp.plugins.api.plugin.yaapp') as mock_yaapp:
            mock_yaapp._config = None
            
            api._load_config()
            
            assert api.config == {}
    
    def test_create_discoverer_openapi(self):
        """Test creating OpenAPI discoverer."""
        config = {
            'type': 'openapi',
            'spec_url': 'https://example.com/api.yaml'
        }
        
        api = Api(config)
        api._load_config()
        discoverer = api._create_discoverer()
        
        assert isinstance(discoverer, OpenAPIDiscoverer)
        assert discoverer.config == config
        assert discoverer.spec_url == 'https://example.com/api.yaml'
    
    def test_create_discoverer_unsupported_type(self):
        """Test creating discoverer with unsupported type."""
        config = {
            'type': 'unsupported',
            'spec_url': 'https://example.com/api.yaml'
        }
        
        api = Api(config)
        api._load_config()
        
        with pytest.raises(ValueError, match="Unsupported API type: unsupported"):
            api._create_discoverer()
    
    def test_create_executor_openapi(self):
        """Test creating OpenAPI executor."""
        config = {
            'type': 'openapi',
            'spec_url': 'https://example.com/api.yaml',
            'base_url': 'http://localhost:8000'
        }
        
        api = Api(config)
        api._load_config()
        api.discoverer = Mock()
        executor = api._create_executor()
        
        assert isinstance(executor, OpenAPIExecutor)
        assert executor.config == config
        assert executor.base_url == 'http://localhost:8000'
    
    @patch('requests.get')
    @patch('yaml.safe_load')
    def test_expose_to_registry_success(self, mock_yaml_load, mock_requests_get):
        """Test successful exposure to registry."""
        # Mock OpenAPI spec
        mock_spec = {
            'swagger': '2.0',
            'paths': {
                '/containers/json': {
                    'get': {
                        'operationId': 'ContainerList',
                        'summary': 'List containers',
                        'parameters': []
                    }
                }
            }
        }
        
        mock_response = Mock()
        mock_response.text = 'mock yaml content'
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response
        mock_yaml_load.return_value = mock_spec
        
        config = {
            'type': 'openapi',
            'spec_url': 'https://example.com/api.yaml',
            'base_url': 'http://localhost:8000'
        }
        
        api = Api(config)
        exposer = Mock()
        
        api.expose_to_registry('api', exposer)
        
        # Verify config was loaded
        assert api.config == config
        
        # Verify discoverer was created
        assert api.discoverer is not None
        assert isinstance(api.discoverer, OpenAPIDiscoverer)
        
        # Verify executor was created
        assert api.executor is not None
        assert isinstance(api.executor, OpenAPIExecutor)
        
        # Verify methods were discovered
        assert len(api._discovered_methods) > 0
        assert 'containers/json' in api._discovered_methods
    
    def test_expose_to_registry_no_config(self):
        """Test exposure to registry with no config."""
        api = Api()
        exposer = Mock()
        
        # Mock yaapp instance without config
        with patch('yaapp.plugins.api.plugin.yaapp') as mock_yaapp:
            mock_yaapp._config = None
            
            api.expose_to_registry('api', exposer)
            
            # Should handle gracefully with empty config
            assert api.config == {}
            assert api._discovered_methods == {}
    
    def test_execute_call_success(self):
        """Test successful execute_call."""
        config = {
            'type': 'openapi',
            'base_url': 'http://localhost:8000'
        }
        
        api = Api(config)
        api._load_config()
        
        # Mock discovered methods
        api._discovered_methods = {
            'containers': {
                'path': '/containers/json',
                'method': 'GET',
                'parameters': []
            }
        }
        
        # Mock executor
        mock_executor = Mock()
        mock_executor.execute.return_value = {'containers': []}
        api.executor = mock_executor
        
        result = api.execute_call('containers')
        
        assert result.is_ok()
        assert result.unwrap() == {'containers': []}
        mock_executor.execute.assert_called_once_with('containers')
    
    def test_execute_call_method_not_found(self):
        """Test execute_call with method not found."""
        api = Api()
        api._discovered_methods = {}
        
        result = api.execute_call('nonexistent')
        
        assert result.is_err()
        assert "Method 'nonexistent' not found" in result.as_error
    
    def test_execute_call_execution_error(self):
        """Test execute_call with execution error."""
        config = {
            'type': 'openapi',
            'base_url': 'http://localhost:8000'
        }
        
        api = Api(config)
        api._load_config()
        
        # Mock discovered methods
        api._discovered_methods = {
            'containers': {
                'path': '/containers/json',
                'method': 'GET',
                'parameters': []
            }
        }
        
        # Mock executor that raises exception
        mock_executor = Mock()
        mock_executor.execute.side_effect = Exception("Connection failed")
        api.executor = mock_executor
        
        result = api.execute_call('containers')
        
        assert result.is_err()
        assert "Connection failed" in result.as_error


class TestOpenAPIDiscoverer:
    """Test the OpenAPI discoverer."""
    
    @patch('requests.get')
    @patch('yaml.safe_load')
    def test_discover_success(self, mock_yaml_load, mock_requests_get):
        """Test successful OpenAPI discovery."""
        # Mock OpenAPI spec
        mock_spec = {
            'swagger': '2.0',
            'paths': {
                '/containers/json': {
                    'get': {
                        'operationId': 'ContainerList',
                        'summary': 'List containers',
                        'parameters': []
                    }
                },
                '/containers/{id}/start': {
                    'post': {
                        'operationId': 'ContainerStart',
                        'summary': 'Start container',
                        'parameters': [
                            {
                                'name': 'id',
                                'in': 'path',
                                'required': True
                            }
                        ]
                    }
                }
            }
        }
        
        mock_response = Mock()
        mock_response.text = 'mock yaml content'
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response
        mock_yaml_load.return_value = mock_spec
        
        config = {
            'spec_url': 'https://example.com/api.yaml'
        }
        
        discoverer = OpenAPIDiscoverer(config)
        methods = discoverer.discover()
        
        # Verify methods were discovered
        assert len(methods) == 2
        assert 'containers/json' in methods
        assert 'containers/start' in methods
        
        # Verify method details
        containers_method = methods['containers/json']
        assert containers_method['path'] == '/containers/json'
        assert containers_method['method'] == 'GET'
        assert containers_method['summary'] == 'List containers'
        
        start_method = methods['containers/start']
        assert start_method['path'] == '/containers/{id}/start'
        assert start_method['method'] == 'POST'
        assert start_method['summary'] == 'Start container'
    
    @patch('requests.get')
    def test_discover_request_failure(self, mock_requests_get):
        """Test OpenAPI discovery with request failure."""
        mock_requests_get.side_effect = Exception("Network error")
        
        config = {
            'spec_url': 'https://example.com/api.yaml'
        }
        
        discoverer = OpenAPIDiscoverer(config)
        
        with pytest.raises(Exception, match="Network error"):
            discoverer.discover()
    
    def test_generate_operation_id_simple_path(self):
        """Test operation ID generation for simple paths."""
        discoverer = OpenAPIDiscoverer({'spec_url': 'test'})
        
        # Test simple paths
        assert discoverer._generate_operation_id('/containers', 'get', {}) == 'containers'
        assert discoverer._generate_operation_id('/images', 'get', {}) == 'images'
    
    def test_generate_operation_id_nested_path(self):
        """Test operation ID generation for nested paths."""
        discoverer = OpenAPIDiscoverer({'spec_url': 'test'})
        
        # Test nested paths
        assert discoverer._generate_operation_id('/containers/json', 'get', {}) == 'containers/json'
        assert discoverer._generate_operation_id('/images/search', 'get', {}) == 'images/search'
    
    def test_generate_operation_id_with_params(self):
        """Test operation ID generation for paths with parameters."""
        discoverer = OpenAPIDiscoverer({'spec_url': 'test'})
        
        # Test paths with parameters
        assert discoverer._generate_operation_id('/containers/{id}/start', 'post', {}) == 'containers/start'
        assert discoverer._generate_operation_id('/containers/{id}/json', 'get', {}) == 'containers/inspect'


class TestOpenAPIExecutor:
    """Test the OpenAPI executor."""
    
    def test_init(self):
        """Test OpenAPI executor initialization."""
        config = {
            'base_url': 'http://localhost:8000',
            'transport': 'http'
        }
        discoverer = Mock()
        
        executor = OpenAPIExecutor(config, discoverer, Mock())
        
        assert executor.config == config
        assert executor.discoverer == discoverer
        assert executor.base_url == 'http://localhost:8000'
        assert executor.transport == 'http'
    
    def test_build_url_simple(self):
        """Test URL building without parameters."""
        config = {'base_url': 'http://localhost:8000'}
        executor = OpenAPIExecutor(config, Mock(), Mock())
        
        url = executor._build_url('/containers/json', {})
        assert url == 'http://localhost:8000/containers/json'
    
    def test_build_url_with_params(self):
        """Test URL building with path parameters."""
        config = {'base_url': 'http://localhost:8000'}
        executor = OpenAPIExecutor(config, Mock(), Mock())
        
        url = executor._build_url('/containers/{id}/start', {'id': 'abc123'})
        assert url == 'http://localhost:8000/containers/abc123/start'
    
    def test_categorize_params(self):
        """Test parameter categorization."""
        config = {'base_url': 'http://localhost:8000'}
        executor = OpenAPIExecutor(config, Mock(), Mock())
        
        method_info = {
            'parameters': [
                {'name': 'id', 'in': 'path'},
                {'name': 'all', 'in': 'query'},
                {'name': 'data', 'in': 'body'}
            ]
        }
        
        kwargs = {
            'id': 'abc123',
            'all': True,
            'data': {'key': 'value'},
            'unknown': 'test'
        }
        
        path_params, query_params, body_params = executor._categorize_params(method_info, kwargs)
        
        assert path_params == {'id': 'abc123'}
        assert query_params == {'all': True, 'unknown': 'test'}
        assert body_params == {'data': {'key': 'value'}}
    
    @patch('requests.request')
    def test_make_request_http(self, mock_request):
        """Test making HTTP request."""
        config = {
            'base_url': 'http://localhost:8000',
            'transport': 'http'
        }
        executor = OpenAPIExecutor(config, Mock(), Mock())
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        result = executor._make_request('GET', 'http://localhost:8000/test', {'param': 'value'})
        
        assert result == mock_response
        mock_request.assert_called_once_with(
            'GET', 
            'http://localhost:8000/test', 
            params={'param': 'value'}, 
            json=None
        )
    
    def test_process_response_json(self):
        """Test processing JSON response."""
        config = {'base_url': 'http://localhost:8000'}
        executor = OpenAPIExecutor(config, Mock(), Mock())
        
        mock_response = Mock()
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {'result': 'success'}
        
        result = executor._process_response(mock_response)
        assert result == {'result': 'success'}
    
    def test_process_response_text(self):
        """Test processing text response."""
        config = {'base_url': 'http://localhost:8000'}
        executor = OpenAPIExecutor(config, Mock(), Mock())
        
        mock_response = Mock()
        mock_response.headers = {'content-type': 'text/plain'}
        mock_response.text = 'success'
        
        result = executor._process_response(mock_response)
        assert result == 'success'
    
    def test_process_response_binary(self):
        """Test processing binary response."""
        config = {'base_url': 'http://localhost:8000'}
        executor = OpenAPIExecutor(config, Mock(), Mock())
        
        mock_response = Mock()
        mock_response.headers = {'content-type': 'application/octet-stream'}
        mock_response.content = b'binary data'
        
        result = executor._process_response(mock_response)
        assert result == b'binary data'