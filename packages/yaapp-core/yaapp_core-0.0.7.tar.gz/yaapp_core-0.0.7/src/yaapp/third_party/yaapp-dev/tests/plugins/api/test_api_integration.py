"""
Integration tests for the API plugin to verify it works end-to-end.
"""

import pytest
from unittest.mock import Mock, patch
from yaapp.plugins.api.plugin import Api


def test_api_plugin_real_docker_discovery():
    """Test that the API plugin can discover real Docker API endpoints."""
    config = {
        'type': 'openapi',
        'spec_url': 'https://raw.githubusercontent.com/docker/engine/master/api/swagger.yaml',
        'base_url': 'http://localhost/v1.42',
        'transport': 'unix_socket',
        'socket_path': '/var/run/docker.sock',
        'description': 'Docker Engine API - Full Docker API with 88+ endpoints for container management'
    }
    
    api = Api(config)
    exposer = Mock()
    
    # This should discover real Docker API endpoints
    api.expose_to_registry('api', exposer)
    
    # Verify config was loaded
    assert api.config == config
    
    # Verify discoverer was created
    assert api.discoverer is not None
    
    # Verify executor was created
    assert api.executor is not None
    
    # Verify methods were discovered (should be many Docker endpoints)
    assert len(api._discovered_methods) > 50  # Docker API has 88+ endpoints
    
    # Check for some expected Docker endpoints
    expected_endpoints = [
        'containers/json',
        'images/json', 
        'version',
        'info'
    ]
    
    for endpoint in expected_endpoints:
        assert endpoint in api._discovered_methods, f"Expected endpoint '{endpoint}' not found in discovered methods"
    
    print(f"✅ Successfully discovered {len(api._discovered_methods)} Docker API endpoints")
    print("Sample endpoints:")
    for i, endpoint in enumerate(list(api._discovered_methods.keys())[:10]):
        print(f"  📡 {endpoint}")
    if len(api._discovered_methods) > 10:
        print(f"  ... and {len(api._discovered_methods) - 10} more")


def test_api_plugin_execute_call_mock():
    """Test that execute_call works with mocked executor."""
    config = {
        'type': 'openapi',
        'base_url': 'http://localhost:8000'
    }
    
    api = Api(config)
    api._load_config()
    
    # Mock discovered methods
    api._discovered_methods = {
        'containers/json': {
            'path': '/containers/json',
            'method': 'GET',
            'parameters': []
        }
    }
    
    # Mock executor
    mock_executor = Mock()
    mock_executor.execute.return_value = [{'Id': 'abc123', 'Names': ['/test']}]
    api.executor = mock_executor
    
    result = api.execute_call('containers/json')
    
    assert result.is_ok()
    containers = result.unwrap()
    assert len(containers) == 1
    assert containers[0]['Id'] == 'abc123'
    assert containers[0]['Names'] == ['/test']
    
    mock_executor.execute.assert_called_once_with('containers/json')


if __name__ == "__main__":
    # Run the real discovery test
    test_api_plugin_real_docker_discovery()