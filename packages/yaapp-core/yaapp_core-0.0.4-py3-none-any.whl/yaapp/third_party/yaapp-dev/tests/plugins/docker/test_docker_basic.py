#!/usr/bin/env python3
"""
Test Docker plugin basic functionality without requiring docker module.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))


class TestDockerBasic:
    """Test Docker plugin basic functionality."""
    
    @pytest.fixture
    def docker_plugin(self):
        """Create a Docker plugin instance for testing."""
        # Mock the docker import to avoid dependency issues
        with patch.dict('sys.modules', {'docker': Mock()}):
            from yaapp.plugins.docker.plugin import Docker
            return Docker({})
    
    @pytest.fixture
    def mock_docker_client(self):
        """Create a mock Docker client."""
        client = Mock()
        client.ping = Mock()
        client.containers = Mock()
        client.images = Mock()
        client.info = Mock()
        client.version = Mock()
        return client
    
    @pytest.mark.asyncio
    async def test_docker_initialization(self, docker_plugin):
        """Test Docker plugin initialization."""
        # Should handle missing Docker daemon gracefully
        assert docker_plugin is not None
        assert docker_plugin.config == {}
    
    @pytest.mark.asyncio
    async def test_ping_with_mock_client(self, docker_plugin, mock_docker_client):
        """Test ping with mock client."""
        docker_plugin.client = mock_docker_client
        mock_docker_client.ping.return_value = True
        
        result = await docker_plugin.ping()
        
        assert result.is_ok()
        assert result.value is True
        mock_docker_client.ping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ping_no_client(self, docker_plugin):
        """Test ping when no client is available."""
        docker_plugin.client = None
        # Prevent reconnection
        docker_plugin._ensure_client = Mock(return_value=False)
        
        result = await docker_plugin.ping()
        
        assert result.is_err()
        assert "Docker daemon not available" in result.as_error
    
    @pytest.mark.asyncio
    async def test_list_containers_with_mock(self, docker_plugin, mock_docker_client):
        """Test container listing with mock client."""
        docker_plugin.client = mock_docker_client
        
        # Mock container
        mock_container = Mock()
        mock_container.id = "test123"
        mock_container.name = "test-container"
        mock_container.status = "running"
        mock_container.image.tags = ["nginx:latest"]
        mock_container.attrs = {"Created": "2023-01-01T00:00:00Z"}
        mock_container.ports = {}
        
        mock_docker_client.containers.list.return_value = [mock_container]
        
        result = await docker_plugin.list_containers()
        
        assert result.is_ok()
        containers = result.value
        assert len(containers) == 1
        assert containers[0]["id"] == "test123"
        assert containers[0]["name"] == "test-container"
        assert containers[0]["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_get_system_info_with_mock(self, docker_plugin, mock_docker_client):
        """Test system info with mock client."""
        docker_plugin.client = mock_docker_client
        
        mock_info = {
            "Containers": 5,
            "ContainersRunning": 3,
            "Images": 10,
            "ServerVersion": "20.10.0"
        }
        mock_docker_client.info.return_value = mock_info
        
        result = await docker_plugin.get_system_info()
        
        assert result.is_ok()
        info = result.value
        assert info["containers"] == 5
        assert info["containers_running"] == 3
        assert info["images"] == 10
        assert info["server_version"] == "20.10.0"
    
    @pytest.mark.asyncio
    async def test_operations_without_client(self, docker_plugin):
        """Test various operations when client is None."""
        docker_plugin.client = None
        # Prevent reconnection
        docker_plugin._ensure_client = Mock(return_value=False)
        
        # Test ping
        ping_result = await docker_plugin.ping()
        assert ping_result.is_err()
        assert "Docker daemon not available" in ping_result.as_error
        
        # Test list containers
        containers_result = await docker_plugin.list_containers()
        assert containers_result.is_err()
        assert "Docker daemon not available" in containers_result.as_error
        
        # Test system info
        info_result = await docker_plugin.get_system_info()
        assert info_result.is_err()
        assert "Docker daemon not available" in info_result.as_error
    
    @pytest.mark.asyncio
    async def test_ensure_client_method(self, docker_plugin):
        """Test the _ensure_client method."""
        # Test when client is None and Docker is not available
        docker_plugin.client = None
        
        # Mock docker.from_env to raise an exception
        with patch('yaapp.plugins.docker.plugin.docker.from_env', side_effect=Exception("Docker not available")):
            result = docker_plugin._ensure_client()
            # Should return False when no Docker daemon available
            assert result is False
        
        # Mock a successful client
        mock_client = Mock()
        mock_client.ping = Mock()
        docker_plugin.client = mock_client
        
        # Should return True when client is available
        result = docker_plugin._ensure_client()
        assert result is True
    
    def test_docker_plugin_config(self, docker_plugin):
        """Test Docker plugin configuration."""
        # Test with empty config
        assert docker_plugin.config == {}
        
        # Test with provided config
        with patch.dict('sys.modules', {'docker': Mock()}):
            from yaapp.plugins.docker.plugin import Docker
            plugin_with_config = Docker({"test": "value"})
            assert plugin_with_config.config == {"test": "value"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])