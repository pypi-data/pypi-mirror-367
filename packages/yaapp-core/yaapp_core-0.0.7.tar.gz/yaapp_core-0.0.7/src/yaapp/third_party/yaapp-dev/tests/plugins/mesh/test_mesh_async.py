#!/usr/bin/env python3
"""
Test Mesh plugin async functionality.
"""

import pytest
import asyncio
import sys
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp.plugins.mesh.plugin import Mesh


class TestMeshAsync:
    """Test Mesh plugin async functionality."""
    
    @pytest.fixture
    def mesh_config(self):
        """Create test mesh configuration."""
        return {
            'registry_integration': True,
            'services': [
                {
                    'name': 'test-service',
                    'command': 'echo "test service"',
                    'port': 8001,
                    'host': 'localhost',
                    'register_with_registry': True
                },
                {
                    'name': 'another-service', 
                    'command': 'sleep 1',
                    'port': 8002,
                    'host': 'localhost',
                    'register_with_registry': False
                }
            ]
        }
    
    @pytest.fixture
    def mesh(self, mesh_config):
        """Create a Mesh instance for testing."""
        return Mesh(mesh_config)
    
    @pytest.fixture
    def mock_registry(self):
        """Create a mock registry for testing."""
        registry = Mock()
        
        # Make the methods async
        async def mock_register(*args, **kwargs):
            return {'status': 'registered'}
        
        async def mock_deregister(*args, **kwargs):
            return {'status': 'deregistered'}
        
        registry.register_service = mock_register
        registry.deregister_service = mock_deregister
        return registry
    
    @pytest.mark.asyncio
    async def test_mesh_initialization(self, mesh):
        """Test mesh initialization."""
        mesh._load_config()
        
        assert mesh.config is not None
        assert mesh.config['registry_integration'] is True
        assert len(mesh.config['services']) == 2
    
    @pytest.mark.asyncio
    async def test_start_service_async(self, mesh, mock_registry):
        """Test async service starting."""
        mesh._load_config()
        mesh._registry = mock_registry
        
        # Mock subprocess.Popen
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None  # Process is running
        
        with patch('subprocess.Popen', return_value=mock_process):
            result = await mesh.start_service('test-service')
        
        assert result['status'] == 'started'
        assert result['service'] == 'test-service'
        assert result['pid'] == 12345
        assert 'test-service' in mesh._running_services
    
    @pytest.mark.asyncio
    async def test_stop_service_async(self, mesh, mock_registry):
        """Test async service stopping."""
        mesh._load_config()
        mesh._registry = mock_registry
        
        # Mock a running process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None  # Process is running
        mock_process.terminate = Mock()
        mock_process.wait = Mock()
        
        # Add to running services
        mesh._running_services['test-service'] = {
            'process': mock_process,
            'started_at': 1234567890,
            'command': 'echo test'
        }
        
        result = await mesh.stop_service('test-service')
        
        assert result['status'] == 'stopped'
        assert result['service'] == 'test-service'
        assert 'test-service' not in mesh._running_services
        mock_process.terminate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_restart_service_async(self, mesh, mock_registry):
        """Test async service restarting."""
        mesh._load_config()
        mesh._registry = mock_registry
        
        # Mock a running process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        mock_process.terminate = Mock()
        mock_process.wait = Mock()
        
        # Add to running services
        mesh._running_services['test-service'] = {
            'process': mock_process,
            'started_at': 1234567890,
            'command': 'echo test'
        }
        
        # Mock new process for restart
        new_mock_process = Mock()
        new_mock_process.pid = 54321
        new_mock_process.poll.return_value = None
        
        with patch('subprocess.Popen', return_value=new_mock_process):
            result = await mesh.restart_service('test-service')
        
        assert result['status'] == 'restarted'
        assert result['service'] == 'test-service'
        assert result['pid'] == 54321
    
    @pytest.mark.asyncio
    async def test_list_services_async(self, mesh):
        """Test async service listing."""
        mesh._load_config()
        
        # Mock some running processes
        mock_process1 = Mock()
        mock_process1.pid = 12345
        mock_process1.poll.return_value = None
        
        mock_process2 = Mock()
        mock_process2.pid = 54321
        mock_process2.poll.return_value = None
        
        mesh._running_services = {
            'service-1': {
                'process': mock_process1,
                'started_at': 1234567890,
                'command': 'echo service1'
            },
            'service-2': {
                'process': mock_process2,
                'started_at': 1234567891,
                'command': 'echo service2'
            }
        }
        
        result = await mesh.list_services()
        
        assert result['total_services'] == 2
        assert len(result['services']) == 2
        
        service_names = [s['name'] for s in result['services']]
        assert 'service-1' in service_names
        assert 'service-2' in service_names
    
    @pytest.mark.asyncio
    async def test_registry_integration_async(self, mesh):
        """Test async registry integration."""
        mesh._load_config()
        
        # Mock registry initialization
        mock_registry = Mock()
        mock_registry.register_service = Mock(return_value={'status': 'registered'})
        
        with patch('yaapp.plugins.registry.plugin.Registry', return_value=mock_registry):
            result = await mesh._init_registry_integration()
            
            assert result.is_ok()
            assert mesh._registry is not None
    
    @pytest.mark.asyncio
    async def test_service_registration_with_registry(self, mesh, mock_registry):
        """Test service registration with registry integration."""
        mesh._load_config()
        mesh._registry = mock_registry
        
        # Mock async registry methods
        async def mock_register(*args, **kwargs):
            return {'status': 'registered'}
        
        mock_registry.register_service = mock_register
        
        # Mock subprocess
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        
        with patch('subprocess.Popen', return_value=mock_process):
            result = await mesh.start_service('test-service')
        
        assert result['status'] == 'started'
        assert result['service'] == 'test-service'
    
    @pytest.mark.asyncio
    async def test_service_deregistration_with_registry(self, mesh, mock_registry):
        """Test service deregistration with registry integration."""
        mesh._load_config()
        mesh._registry = mock_registry
        
        # Mock async registry methods
        async def mock_deregister(*args, **kwargs):
            return {'status': 'deregistered'}
        
        mock_registry.deregister_service = mock_deregister
        
        # Mock running process
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.poll.return_value = None
        mock_process.terminate = Mock()
        mock_process.wait = Mock()
        
        mesh._running_services['test-service'] = {
            'process': mock_process,
            'started_at': 1234567890,
            'command': 'echo test'
        }
        
        result = await mesh.stop_service('test-service')
        
        assert result['status'] == 'stopped'
        assert result['service'] == 'test-service'
    
    @pytest.mark.asyncio
    async def test_start_nonexistent_service(self, mesh):
        """Test starting a service that's not in configuration."""
        mesh._load_config()
        
        result = await mesh.start_service('nonexistent-service')
        
        assert result['status'] == 'error'
        assert 'not found' in result['error']
    
    @pytest.mark.asyncio
    async def test_stop_nonexistent_service(self, mesh):
        """Test stopping a service that's not running."""
        mesh._load_config()
        
        result = await mesh.stop_service('nonexistent-service')
        
        assert result['status'] == 'not_running'
        assert result['service'] == 'nonexistent-service'
    
    @pytest.mark.asyncio
    async def test_concurrent_service_operations(self, mesh, mock_registry):
        """Test concurrent service operations."""
        mesh._load_config()
        mesh._registry = mock_registry
        
        # Mock processes
        mock_processes = []
        for i in range(3):
            mock_process = Mock()
            mock_process.pid = 12345 + i
            mock_process.poll.return_value = None
            mock_processes.append(mock_process)
        
        with patch('subprocess.Popen', side_effect=mock_processes):
            # Start multiple services concurrently
            tasks = [
                mesh.start_service('test-service'),
                mesh.start_service('another-service')
            ]
            
            # Note: We can only start services that exist in config
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # At least one should succeed (test-service exists in config)
            success_count = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'started')
            assert success_count >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])