#!/usr/bin/env python3
"""
Simple Docker plugin tests focusing on async behavior.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))


class TestDockerSimple:
    """Simple Docker plugin tests."""
    
    def test_docker_plugin_import(self):
        """Test that Docker plugin can be imported."""
        with patch.dict('sys.modules', {'docker': Mock()}):
            from yaapp.plugins.docker.plugin import Docker
            plugin = Docker({})
            assert plugin is not None
    
    @pytest.mark.asyncio
    async def test_async_methods_exist(self):
        """Test that async methods exist and are callable."""
        with patch.dict('sys.modules', {'docker': Mock()}):
            from yaapp.plugins.docker.plugin import Docker
            plugin = Docker({})
            
            # Check that methods are async
            assert asyncio.iscoroutinefunction(plugin.ping)
            assert asyncio.iscoroutinefunction(plugin.list_containers)
            assert asyncio.iscoroutinefunction(plugin.get_system_info)
            assert asyncio.iscoroutinefunction(plugin.get_version)
            assert asyncio.iscoroutinefunction(plugin.start_container)
    
    @pytest.mark.asyncio
    async def test_mock_docker_operations(self):
        """Test Docker operations with fully mocked client."""
        # Mock the entire docker module
        mock_docker = Mock()
        mock_client = Mock()
        mock_docker.from_env.return_value = mock_client
        
        with patch.dict('sys.modules', {'docker': mock_docker}):
            from yaapp.plugins.docker.plugin import Docker
            
            # Create plugin and manually set client
            plugin = Docker({})
            plugin.client = mock_client
            
            # Mock client methods
            mock_client.ping.return_value = True
            mock_client.info.return_value = {"Containers": 5}
            mock_client.version.return_value = {"Version": "20.10.0"}
            mock_client.containers.list.return_value = []
            
            # Test async operations
            ping_result = await plugin.ping()
            info_result = await plugin.get_system_info()
            version_result = await plugin.get_version()
            containers_result = await plugin.list_containers()
            
            # All should succeed
            assert ping_result.is_ok()
            assert info_result.is_ok()
            assert version_result.is_ok()
            assert containers_result.is_ok()
    
    def test_docker_plugin_configuration(self):
        """Test Docker plugin configuration handling."""
        with patch.dict('sys.modules', {'docker': Mock()}):
            from yaapp.plugins.docker.plugin import Docker
            
            # Test with no config
            plugin1 = Docker()
            assert plugin1.config == {}
            
            # Test with config
            config = {"host": "localhost", "port": 2376}
            plugin2 = Docker(config)
            assert plugin2.config == config
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in async methods."""
        # Mock docker module with failing client
        mock_docker = Mock()
        mock_client = Mock()
        mock_docker.from_env.return_value = mock_client
        
        with patch.dict('sys.modules', {'docker': mock_docker}):
            from yaapp.plugins.docker.plugin import Docker
            
            plugin = Docker({})
            plugin.client = mock_client
            
            # Mock client method to raise exception
            mock_client.ping.side_effect = Exception("Connection failed")
            
            result = await plugin.ping()
            
            assert result.is_err()
            assert "Connection failed" in result.as_error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])