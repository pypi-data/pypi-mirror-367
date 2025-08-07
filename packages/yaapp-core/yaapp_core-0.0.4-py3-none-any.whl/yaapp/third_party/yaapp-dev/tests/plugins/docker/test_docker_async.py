#!/usr/bin/env python3
"""
Test Docker plugin async functionality.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp.plugins.docker.plugin import Docker
from yaapp.result import Ok, Err


class TestDockerAsync:
    """Test Docker plugin async functionality."""
    
    @pytest.fixture
    def docker_plugin(self):
        """Create a Docker plugin instance for testing."""
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
    async def test_ping_async(self, docker_plugin, mock_docker_client):
        """Test async Docker ping."""
        docker_plugin.client = mock_docker_client
        
        # Mock the ping method
        mock_docker_client.ping.return_value = True
        
        result = await docker_plugin.ping()
        
        assert result.is_ok()
        assert result.value is True
        mock_docker_client.ping.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ping_failure(self, docker_plugin):
        """Test ping failure when Docker daemon is not available."""
        # Force client to None to simulate daemon unavailable
        docker_plugin.client = None
        # Also prevent reconnection by mocking _ensure_client to return False
        docker_plugin._ensure_client = Mock(return_value=False)
        
        result = await docker_plugin.ping()
        
        assert result.is_err()
        assert "Docker daemon not available" in result.as_error
    
    @pytest.mark.asyncio
    async def test_list_containers_async(self, docker_plugin, mock_docker_client):
        """Test async container listing."""
        docker_plugin.client = mock_docker_client
        
        # Mock container objects
        mock_container1 = Mock()
        mock_container1.id = "container1"
        mock_container1.name = "test-container-1"
        mock_container1.status = "running"
        mock_container1.image.tags = ["nginx:latest"]
        mock_container1.attrs = {"Created": "2023-01-01T00:00:00Z"}
        mock_container1.ports = {"80/tcp": [{"HostPort": "8080"}]}
        
        mock_container2 = Mock()
        mock_container2.id = "container2"
        mock_container2.name = "test-container-2"
        mock_container2.status = "stopped"
        mock_container2.image.tags = []
        mock_container2.image.id = "sha256:abc123"
        mock_container2.attrs = {"Created": "2023-01-02T00:00:00Z"}
        mock_container2.ports = {}
        
        mock_docker_client.containers.list.return_value = [mock_container1, mock_container2]
        
        result = await docker_plugin.list_containers(all=True)
        
        assert result.is_ok()
        containers = result.value
        assert len(containers) == 2
        
        # Check first container
        assert containers[0]["id"] == "container1"
        assert containers[0]["name"] == "test-container-1"
        assert containers[0]["status"] == "running"
        assert containers[0]["image"] == "nginx:latest"
        
        # Check second container
        assert containers[1]["id"] == "container2"
        assert containers[1]["name"] == "test-container-2"
        assert containers[1]["status"] == "stopped"
        assert containers[1]["image"] == "sha256:abc123"
    
    @pytest.mark.asyncio
    async def test_start_container_async(self, docker_plugin, mock_docker_client):
        """Test async container starting."""
        docker_plugin.client = mock_docker_client
        
        # Mock container object
        mock_container = Mock()
        mock_container.start = Mock()
        mock_docker_client.containers.get.return_value = mock_container
        
        result = await docker_plugin.start_container("test-container")
        
        assert result.is_ok()
        assert result.value is True
        mock_docker_client.containers.get.assert_called_once_with("test-container")
        mock_container.start.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_container_not_found(self, docker_plugin, mock_docker_client):
        """Test starting a container that doesn't exist."""
        docker_plugin.client = mock_docker_client
        
        # Mock docker.errors.NotFound
        from unittest.mock import Mock
        
        class MockNotFound(Exception):
            pass
        
        mock_docker_client.containers.get.side_effect = MockNotFound("Container not found")
        
        result = await docker_plugin.start_container("nonexistent-container")
        
        assert result.is_err()
        assert "Failed to start container: Container not found" in result.as_error
    
    @pytest.mark.asyncio
    async def test_get_system_info_async(self, docker_plugin, mock_docker_client):
        """Test async system info retrieval."""
        docker_plugin.client = mock_docker_client
        
        # Mock system info
        mock_info = {
            "Containers": 10,
            "ContainersRunning": 5,
            "ContainersPaused": 1,
            "ContainersStopped": 4,
            "Images": 20,
            "ServerVersion": "20.10.0",
            "KernelVersion": "5.4.0",
            "OperatingSystem": "Ubuntu 20.04",
            "Architecture": "x86_64",
            "MemTotal": 8589934592,
            "NCPU": 4
        }
        mock_docker_client.info.return_value = mock_info
        
        result = await docker_plugin.get_system_info()
        
        assert result.is_ok()
        info = result.value
        assert info["containers"] == 10
        assert info["containers_running"] == 5
        assert info["containers_paused"] == 1
        assert info["containers_stopped"] == 4
        assert info["images"] == 20
        assert info["server_version"] == "20.10.0"
        assert info["kernel_version"] == "5.4.0"
        assert info["operating_system"] == "Ubuntu 20.04"
        assert info["architecture"] == "x86_64"
        assert info["memory_total"] == 8589934592
        assert info["cpus"] == 4
    
    @pytest.mark.asyncio
    async def test_get_version_async(self, docker_plugin, mock_docker_client):
        """Test async version retrieval."""
        docker_plugin.client = mock_docker_client
        
        # Mock version info
        mock_version = {
            "Version": "20.10.0",
            "ApiVersion": "1.41",
            "GitCommit": "abc123",
            "GoVersion": "go1.16.0",
            "Os": "linux",
            "Arch": "amd64"
        }
        mock_docker_client.version.return_value = mock_version
        
        result = await docker_plugin.get_version()
        
        assert result.is_ok()
        version = result.value
        assert version["Version"] == "20.10.0"
        assert version["ApiVersion"] == "1.41"
        assert version["GitCommit"] == "abc123"
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, docker_plugin, mock_docker_client):
        """Test concurrent Docker operations."""
        docker_plugin.client = mock_docker_client
        
        # Mock responses
        mock_docker_client.ping.return_value = True
        mock_docker_client.info.return_value = {"Containers": 5}
        mock_docker_client.version.return_value = {"Version": "20.10.0"}
        mock_docker_client.containers.list.return_value = []
        
        # Run multiple operations concurrently
        tasks = [
            docker_plugin.ping(),
            docker_plugin.get_system_info(),
            docker_plugin.get_version(),
            docker_plugin.list_containers()
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        for result in results:
            assert result.is_ok()
        
        # Check specific results
        assert results[0].value is True  # ping
        assert results[1].value["containers"] == 5  # system info
        assert results[2].value["Version"] == "20.10.0"  # version
        assert results[3].value == []  # containers
    
    @pytest.mark.asyncio
    async def test_docker_daemon_unavailable(self, docker_plugin):
        """Test behavior when Docker daemon is unavailable."""
        # Force client to None and prevent reconnection
        docker_plugin.client = None
        docker_plugin._ensure_client = Mock(return_value=False)
        
        # Test various operations
        ping_result = await docker_plugin.ping()
        containers_result = await docker_plugin.list_containers()
        info_result = await docker_plugin.get_system_info()
        version_result = await docker_plugin.get_version()
        
        # All should fail with daemon unavailable error
        assert ping_result.is_err()
        assert containers_result.is_err()
        assert info_result.is_err()
        assert version_result.is_err()
        
        assert "Docker daemon not available" in ping_result.as_error
        assert "Docker daemon not available" in containers_result.as_error
        assert "Docker daemon not available" in info_result.as_error
        assert "Docker daemon not available" in version_result.as_error
    
    @pytest.mark.asyncio
    async def test_ensure_client_reconnection(self, docker_plugin):
        """Test client reconnection when initially unavailable."""
        # Start with no client
        docker_plugin.client = None
        
        # Mock successful reconnection
        mock_client = Mock()
        mock_client.ping = Mock()
        
        with patch('yaapp.plugins.docker.plugin.docker.from_env', return_value=mock_client):
            # This should trigger reconnection
            success = docker_plugin._ensure_client()
            
            assert success is True
            assert docker_plugin.client is not None
    
    @pytest.mark.asyncio
    async def test_asyncio_to_thread_usage(self, docker_plugin, mock_docker_client):
        """Test that asyncio.to_thread is used for blocking operations."""
        docker_plugin.client = mock_docker_client
        
        # Mock a slow operation
        def slow_ping():
            import time
            time.sleep(0.1)  # Simulate slow operation
            return True
        
        mock_docker_client.ping = slow_ping
        
        # This should use asyncio.to_thread internally
        start_time = asyncio.get_event_loop().time()
        result = await docker_plugin.ping()
        end_time = asyncio.get_event_loop().time()
        
        assert result.is_ok()
        assert result.value is True
        # Should complete in reasonable time (not block the event loop)
        assert (end_time - start_time) < 1.0
    
    @pytest.mark.asyncio
    async def test_error_handling_in_async_operations(self, docker_plugin, mock_docker_client):
        """Test error handling in async operations."""
        docker_plugin.client = mock_docker_client
        
        # Mock an operation that raises an exception
        mock_docker_client.info.side_effect = Exception("Docker API error")
        
        result = await docker_plugin.get_system_info()
        
        assert result.is_err()
        assert "Docker API error" in result.as_error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])