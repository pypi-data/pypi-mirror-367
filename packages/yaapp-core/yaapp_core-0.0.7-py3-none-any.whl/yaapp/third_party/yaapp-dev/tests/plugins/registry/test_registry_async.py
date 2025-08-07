#!/usr/bin/env python3
"""
Test Registry plugin async functionality.
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp.plugins.registry.plugin import Registry


class TestRegistryAsync:
    """Test Registry plugin async functionality."""
    
    @pytest.fixture
    def registry(self):
        """Create a Registry instance for testing."""
        return Registry({})
    
    @pytest.mark.asyncio
    async def test_register_service_async(self, registry):
        """Test async service registration."""
        registry._load_config()
        
        result = await registry.register_service(
            service_name="test-service",
            instance_id="instance-1", 
            host="localhost",
            port=8001,
            metadata={"version": "1.0"}
        )
        
        assert result["status"] == "registered"
        assert result["service_name"] == "test-service"
        assert result["instance_id"] == "instance-1"
    
    @pytest.mark.asyncio
    async def test_discover_service_async(self, registry):
        """Test async service discovery."""
        registry._load_config()
        
        # Register a service first
        await registry.register_service("test-service", "instance-1", "localhost", 8001)
        
        # Discover it
        result = await registry.discover_service("test-service")
        
        assert result["service_name"] == "test-service"
        assert result["total_instances"] == 1
        assert len(result["instances"]) == 1
        assert result["instances"][0]["instance_id"] == "instance-1"
    
    @pytest.mark.asyncio
    async def test_list_services_async(self, registry):
        """Test async service listing."""
        registry._load_config()
        
        # Register multiple services
        await registry.register_service("service-1", "instance-1", "localhost", 8001)
        await registry.register_service("service-2", "instance-1", "localhost", 8002)
        
        result = await registry.list_services()
        
        assert result["total_services"] == 2
        assert result["total_instances"] == 2
        
        service_names = [s["service_name"] for s in result["services"]]
        assert "service-1" in service_names
        assert "service-2" in service_names
    
    @pytest.mark.asyncio
    async def test_deregister_service_async(self, registry):
        """Test async service deregistration."""
        registry._load_config()
        
        # Register a service
        await registry.register_service("test-service", "instance-1", "localhost", 8001)
        
        # Verify it exists
        discovery = await registry.discover_service("test-service")
        assert discovery["total_instances"] == 1
        
        # Deregister it
        result = await registry.deregister_service("test-service", "instance-1")
        assert result["status"] == "deregistered"
        
        # Verify it's gone
        discovery = await registry.discover_service("test-service")
        assert discovery["total_instances"] == 0
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, registry):
        """Test concurrent async operations."""
        registry._load_config()
        
        # Register multiple services concurrently
        tasks = []
        for i in range(5):
            task = registry.register_service(f"service-{i}", "instance-1", "localhost", 8000 + i)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        for result in results:
            assert result["status"] == "registered"
        
        # Verify all are listed
        list_result = await registry.list_services()
        assert list_result["total_services"] == 5
    
    @pytest.mark.asyncio
    async def test_discover_nonexistent_service(self, registry):
        """Test discovering a service that doesn't exist."""
        registry._load_config()
        
        result = await registry.discover_service("nonexistent-service")
        
        assert result["service_name"] == "nonexistent-service"
        assert result["total_instances"] == 0
        assert result["instances"] == []
    
    @pytest.mark.asyncio
    async def test_deregister_nonexistent_service(self, registry):
        """Test deregistering a service that doesn't exist."""
        registry._load_config()
        
        result = await registry.deregister_service("nonexistent-service", "instance-1")
        
        assert result["status"] == "service_not_found"
        assert result["service_name"] == "nonexistent-service"
    
    @pytest.mark.asyncio
    async def test_multiple_instances_same_service(self, registry):
        """Test multiple instances of the same service."""
        registry._load_config()
        
        # Register multiple instances
        await registry.register_service("web-service", "instance-1", "localhost", 8001)
        await registry.register_service("web-service", "instance-2", "localhost", 8002)
        await registry.register_service("web-service", "instance-3", "localhost", 8003)
        
        # Discover the service
        result = await registry.discover_service("web-service")
        
        assert result["total_instances"] == 3
        assert len(result["instances"]) == 3
        
        # Check all instances are there
        instance_ids = [inst["instance_id"] for inst in result["instances"]]
        assert "instance-1" in instance_ids
        assert "instance-2" in instance_ids
        assert "instance-3" in instance_ids
    
    @pytest.mark.asyncio
    async def test_service_metadata(self, registry):
        """Test service metadata handling."""
        registry._load_config()
        
        metadata = {
            "version": "1.2.3",
            "environment": "production",
            "health_check": "/health"
        }
        
        await registry.register_service(
            "api-service", "instance-1", "localhost", 8001, metadata
        )
        
        result = await registry.discover_service("api-service")
        
        assert result["total_instances"] == 1
        instance = result["instances"][0]
        assert instance["metadata"] == metadata


if __name__ == "__main__":
    pytest.main([__file__, "-v"])