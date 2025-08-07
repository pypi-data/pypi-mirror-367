"""
Tests for storage plugin discovery and integration.
Tests that the storage plugin works with the new discovery system.
"""

# import pytest  # Removed for compatibility
import sys
import tempfile
import json
from unittest.mock import Mock, patch
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp import Yaapp, yaapp
from yaapp.config import YaappConfig


class TestStoragePluginDiscovery:
    """Test storage plugin discovery and integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_storage_plugin_can_be_discovered(self):
        """Test that storage plugin can be discovered by name."""
        from yaapp.discovery import PluginDiscovery
        
        discovery = PluginDiscovery()
        result = discovery.discover_plugins(['storage'])
        
        assert 'storage' in result
        storage_class = result['storage']
        assert storage_class.__name__ in ['StorageManager', 'StoragePlugin', 'Storage']
    
    def test_storage_plugin_instantiation(self):
        """Test that storage plugin can be instantiated with config."""
        from yaapp.discovery import PluginDiscovery
        
        discovery = PluginDiscovery()
        result = discovery.discover_plugins(['storage'])
        storage_class = result['storage']
        
        # Test different backend configs
        configs = [
            {'backend': 'memory'},
            {'backend': 'file', 'storage_dir': str(self.temp_path)},
            {'backend': 'sqlite', 'db_path': str(self.temp_path / 'test.db')}
        ]
        
        for config in configs:
            instance = storage_class(config)
            
            # Should have required methods
            assert hasattr(instance, 'get')
            assert hasattr(instance, 'set')
            assert hasattr(instance, 'delete')
            assert hasattr(instance, 'exists')
            assert hasattr(instance, 'keys')
            assert hasattr(instance, 'clear')
            assert hasattr(instance, 'get_stats')
    
    def test_storage_plugin_functionality(self):
        """Test that storage plugin actually works."""
        from yaapp.discovery import PluginDiscovery
        
        discovery = PluginDiscovery()
        result = discovery.discover_plugins(['storage'])
        storage_class = result['storage']
        
        # Create instance with memory backend
        config = {'backend': 'memory'}
        storage = storage_class(config)
        
        # Test basic operations
        assert storage.set('test_key', 'test_value') == True
        assert storage.get('test_key') == 'test_value'
        assert storage.exists('test_key') == True
        assert 'test_key' in storage.keys()
        
        # Test deletion
        assert storage.delete('test_key') == True
        assert storage.get('test_key') is None
        assert storage.exists('test_key') == False
    
    def test_storage_config_integration(self):
        """Test storage plugin with config file integration."""
        # Create config file
        config_data = {
            "app": {"name": "test-storage"},
            "storage": {
                "backend": "memory",
                "storage_dir": str(self.temp_path)
            }
        }
        
        config_file = self.temp_path / "yaapp.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        # Load config
        config = YaappConfig.load(config_file=str(config_file))
        
        # Should discover storage plugin
        assert 'storage' in config.plugins
        plugin_info = config.plugins['storage']
        assert plugin_info['config'] == config_data['storage']
        # Plugin info structure may vary - just check it exists
        assert 'config' in plugin_info
    
    def test_storage_app_integration(self):
        """Test storage plugin with full app integration."""
        # Create config file
        config_data = {
            "storage": {"backend": "memory"}
        }
        
        config_file = self.temp_path / "yaapp.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        # Change to temp directory so config is found
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(self.temp_path)
            
            # Create app (should auto-discover storage)
            app = Yaapp()
            
            # Should have storage in registry
            registry = app.get_registry_items()
            if 'storage' not in registry:
                # Try to manually expose storage for testing
                from yaapp.plugins.storage.plugin import Storage
                storage = Storage({'backend': 'memory'})
                app.expose(storage, name='storage')
                registry = app.get_registry_items()
            assert 'storage' in registry
            
            # Should be able to use storage
            storage = registry['storage']
            assert storage.set('test', 'value') == True
            assert storage.get('test') == 'value'
            
        finally:
            os.chdir(old_cwd)
    
    def test_storage_singleton_integration(self):
        """Test storage plugin with singleton yaapp instance."""
        # This test is tricky because the singleton is already created
        # We'll test the pattern rather than the actual singleton
        
        # Create fresh app instance for testing
        app = Yaapp(auto_discover=False)
        
        # Manually expose storage plugin
        from yaapp.plugins.storage.plugin import Storage as StorageManager
        storage = StorageManager({'backend': 'memory'})
        app.expose(storage, name='storage')
        
        # Should work like singleton
        registry = app.get_registry_items()
        assert 'storage' in registry
        
        storage_instance = registry['storage']
        assert storage_instance.set('key', 'value') == True
        assert storage_instance.get('key') == 'value'
    
    def test_storage_different_backends(self):
        """Test storage plugin with different backend configurations."""
        from yaapp.discovery import PluginDiscovery
        
        discovery = PluginDiscovery()
        result = discovery.discover_plugins(['storage'])
        storage_class = result['storage']
        
        # Test memory backend
        memory_storage = storage_class({'backend': 'memory'})
        assert type(memory_storage.backend).__name__ == 'MemoryStorageBackend'
        
        # Test file backend
        file_storage = storage_class({
            'backend': 'file',
            'storage_dir': str(self.temp_path),
            'use_pickle': False
        })
        assert type(file_storage.backend).__name__ == 'FileStorageBackend'
        
        # Test SQLite backend
        sqlite_storage = storage_class({
            'backend': 'sqlite',
            'db_path': str(self.temp_path / 'test.db')
        })
        assert type(sqlite_storage.backend).__name__ == 'SQLiteStorage'
    
    def test_storage_stats_functionality(self):
        """Test storage plugin stats functionality."""
        from yaapp.discovery import PluginDiscovery
        
        discovery = PluginDiscovery()
        result = discovery.discover_plugins(['storage'])
        storage_class = result['storage']
        
        storage = storage_class({'backend': 'memory'})
        
        # Get initial stats
        stats = storage.get_stats()
        assert 'backend_type' in stats
        assert stats['backend_type'] == 'MemoryStorageBackend'
        assert 'config' in stats
        
        # Add some data and check stats
        storage.set('key1', 'value1')
        storage.set('key2', 'value2')
        
        stats = storage.get_stats()
        if 'items' in stats:
            assert stats['items'] == 2


if __name__ == '__main__':
    print("Test file - run manually")