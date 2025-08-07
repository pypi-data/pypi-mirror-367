#!/usr/bin/env python3
"""
Test PortAlloc plugin basic functionality.
"""

import pytest
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp.plugins.portalloc.plugin import PortAlloc


class TestPortAllocBasic:
    """Test PortAlloc plugin basic functionality."""
    
    @pytest.fixture
    def portalloc_config(self):
        """Create test portalloc configuration."""
        return {
            'port_range': '9000-9010',
            'host': 'localhost',
            'default_lease_time': 3600,
            'persistence_file': tempfile.mktemp(suffix='.json')
        }
    
    @pytest.fixture
    def portalloc(self, portalloc_config):
        """Create a PortAlloc instance for testing."""
        return PortAlloc(portalloc_config)
    
    def test_portalloc_initialization(self, portalloc):
        """Test portalloc initialization."""
        portalloc._load_config()
        
        assert portalloc.config is not None
        assert portalloc.config['port_range'] == '9000-9010'
        assert portalloc.config['host'] == 'localhost'
        assert portalloc.config['default_lease_time'] == 3600
    
    def test_parse_port_range(self, portalloc):
        """Test port range parsing."""
        portalloc._load_config()
        
        port_range = portalloc._parse_port_range()
        
        assert port_range == list(range(9000, 9011))  # 9000-9010 inclusive
        assert len(port_range) == 11
    
    def test_allocate_port_basic(self, portalloc):
        """Test basic port allocation."""
        portalloc._load_config()
        
        # Mock port availability check to always return True
        with patch.object(portalloc, '_is_port_available', return_value=True):
            result = portalloc.allocate_port('test-service')
        
        assert result['status'] == 'allocated'
        assert result['service'] == 'test-service'
        assert 'port' in result
        assert 9000 <= result['port'] <= 9010
        assert 'lease_expires_at' in result
    
    def test_allocate_preferred_port(self, portalloc):
        """Test allocating a preferred port."""
        portalloc._load_config()
        
        with patch.object(portalloc, '_is_port_available', return_value=True):
            result = portalloc.allocate_port('test-service', preferred_port=9005)
        
        assert result['status'] == 'allocated'
        assert result['port'] == 9005
        assert result['service'] == 'test-service'
    
    def test_allocate_port_outside_range(self, portalloc):
        """Test allocating a preferred port outside the range."""
        portalloc._load_config()
        
        with patch.object(portalloc, '_is_port_available', return_value=True):
            # Mock _scan_for_available_port to return a port in range
            with patch.object(portalloc, '_scan_for_available_port', return_value=9001):
                result = portalloc.allocate_port('test-service', preferred_port=8000)  # Outside range
        
        assert result['status'] == 'allocated'
        assert result['port'] == 9001  # Should get a port in range instead
        assert result['service'] == 'test-service'
    
    def test_release_port_by_number(self, portalloc):
        """Test releasing a port by port number."""
        portalloc._load_config()
        
        # First allocate a port
        with patch.object(portalloc, '_is_port_available', return_value=True):
            alloc_result = portalloc.allocate_port('test-service')
        
        allocated_port = alloc_result['port']
        
        # Then release it
        result = portalloc.release_port(str(allocated_port))
        
        assert result['status'] == 'released'
        assert result['port'] == allocated_port
        assert result['service'] == 'test-service'
    
    def test_release_port_by_service_name(self, portalloc):
        """Test releasing a port by service name."""
        portalloc._load_config()
        
        # First allocate a port
        with patch.object(portalloc, '_is_port_available', return_value=True):
            alloc_result = portalloc.allocate_port('test-service')
        
        allocated_port = alloc_result['port']
        
        # Then release it by service name
        result = portalloc.release_port('test-service')
        
        assert result['status'] == 'released'
        assert result['port'] == allocated_port
        assert result['service'] == 'test-service'
    
    def test_list_allocations(self, portalloc):
        """Test listing allocations."""
        portalloc._load_config()
        
        # Allocate multiple ports
        with patch.object(portalloc, '_is_port_available', return_value=True):
            portalloc.allocate_port('service-1')
            portalloc.allocate_port('service-2')
            portalloc.allocate_port('service-3')
        
        result = portalloc.list_allocations()
        
        assert result['total_allocated'] == 3
        assert len(result['allocations']) == 3
        assert result['port_range'] == '9000-9010'
        
        # Check that all services are listed
        service_names = [alloc['service'] for alloc in result['allocations']]
        assert 'service-1' in service_names
        assert 'service-2' in service_names
        assert 'service-3' in service_names
    
    def test_scan_ports(self, portalloc):
        """Test port scanning functionality."""
        portalloc._load_config()
        
        # Mock port availability - some available, some not
        def mock_is_available(host, port):
            return port % 2 == 0  # Even ports available, odd ports not
        
        with patch.object(portalloc, '_is_port_available', side_effect=mock_is_available):
            result = portalloc.scan_ports()
        
        assert 'range' in result
        assert result['total_ports'] == 11  # 9000-9010
        assert 'available' in result
        assert 'unavailable' in result
        assert 'summary' in result
        
        # Check that even ports are available
        available_ports = result['available']
        for port in available_ports:
            assert port % 2 == 0
    
    def test_check_port(self, portalloc):
        """Test checking a specific port."""
        portalloc._load_config()
        
        # Test available port
        with patch.object(portalloc, '_is_port_available', return_value=True):
            result = portalloc.check_port(9005)
        
        assert result['port'] == 9005
        assert result['status'] == 'available'
        assert result['host'] == 'localhost'
    
    def test_check_allocated_port(self, portalloc):
        """Test checking a port that's already allocated."""
        portalloc._load_config()
        
        # Allocate a port first
        with patch.object(portalloc, '_is_port_available', return_value=True):
            portalloc.allocate_port('test-service', preferred_port=9005)
        
        # Check the allocated port
        result = portalloc.check_port(9005)
        
        assert result['port'] == 9005
        assert result['status'] == 'allocated_by_portalloc'
        assert result['service'] == 'test-service'
        assert 'allocated_at' in result
        assert 'expires_at' in result
    
    def test_cleanup_expired(self, portalloc):
        """Test cleanup of expired allocations."""
        portalloc._load_config()
        
        # Allocate a port with short lease
        with patch.object(portalloc, '_is_port_available', return_value=True):
            portalloc.allocate_port('test-service', lease_time=1)  # 1 second lease
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Cleanup expired
        result = portalloc.cleanup_expired()
        
        assert result['cleaned_count'] == 1
        assert len(result['expired_allocations']) == 1
        assert result['expired_allocations'][0]['service'] == 'test-service'
    
    def test_renew_existing_allocation(self, portalloc):
        """Test renewing an existing allocation."""
        portalloc._load_config()
        
        # Allocate a port
        with patch.object(portalloc, '_is_port_available', return_value=True):
            first_result = portalloc.allocate_port('test-service')
        
        allocated_port = first_result['port']
        
        # Allocate again for the same service (should renew)
        with patch.object(portalloc, '_is_port_available', return_value=True):
            second_result = portalloc.allocate_port('test-service', lease_time=7200)
        
        assert second_result['status'] == 'renewed'
        assert second_result['port'] == allocated_port  # Same port
        assert second_result['service'] == 'test-service'
    
    def test_no_available_ports(self, portalloc):
        """Test behavior when no ports are available."""
        portalloc._load_config()
        
        # Mock all ports as unavailable
        with patch.object(portalloc, '_is_port_available', return_value=False):
            with patch.object(portalloc, '_scan_for_available_port', return_value=None):
                result = portalloc.allocate_port('test-service')
        
        assert 'error' in result
        assert 'No available ports' in result['error']
        assert result['allocated_ports'] == 0
        assert result['total_range'] == 11
    
    def test_release_nonexistent_port(self, portalloc):
        """Test releasing a port that's not allocated."""
        portalloc._load_config()
        
        result = portalloc.release_port('9999')
        
        assert 'error' in result
        assert 'not allocated' in result['error']
    
    def test_release_nonexistent_service(self, portalloc):
        """Test releasing a service that has no allocated port."""
        portalloc._load_config()
        
        result = portalloc.release_port('nonexistent-service')
        
        assert 'error' in result
        assert 'has no allocated port' in result['error']
    
    def test_custom_port_range(self, portalloc):
        """Test scanning with custom port range."""
        portalloc._load_config()
        
        with patch.object(portalloc, '_is_port_available', return_value=True):
            result = portalloc.scan_ports(start_port=8000, end_port=8005)
        
        assert result['range'] == '8000-8005'
        assert result['total_ports'] == 6  # 8000-8005 inclusive
        assert len(result['available']) == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])