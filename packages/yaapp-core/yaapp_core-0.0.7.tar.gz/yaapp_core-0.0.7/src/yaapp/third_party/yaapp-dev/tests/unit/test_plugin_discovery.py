"""
Unit tests for the plugin discovery system.
Tests the PluginDiscovery class and its naming strategies.
"""

import pytest
from unittest.mock import Mock, patch, call
from yaapp.discovery import PluginDiscovery


class TestPluginDiscovery:
    """Test the PluginDiscovery class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.discovery = PluginDiscovery()
    
    def test_init(self):
        """Test PluginDiscovery initialization."""
        assert self.discovery._plugin_cache == {}
        assert 'yaapp.plugins' in self.discovery._search_paths
        assert 'yaapp_plugins' in self.discovery._search_paths
    
    def test_discover_plugins_empty(self):
        """Test discovering plugins with empty section list."""
        result = self.discovery.discover_plugins([])
        assert result == {}
    
    def test_discover_plugins_cached(self):
        """Test that cached plugins are returned."""
        # Pre-populate cache
        mock_class = Mock()
        self.discovery._plugin_cache['storage'] = mock_class
        
        result = self.discovery.discover_plugins(['storage'])
        assert result == {'storage': mock_class}
    
    @patch('yaapp.discovery.importlib.import_module')
    def test_find_plugin_class_direct_match(self, mock_import):
        """Test finding plugin with direct name match."""
        # Mock module with StoragePlugin class
        mock_module = Mock()
        mock_class = Mock()
        mock_module.StoragePlugin = mock_class
        mock_import.return_value = mock_module
        
        result = self.discovery._find_plugin_class('storage')
        
        assert result == mock_class
        # The discovery system now tries .plugin first, then the direct module
        expected_calls = [
            call('yaapp.plugins.storage.plugin'),
            call('yaapp.plugins.storage')
        ]
        # Check that at least one of the expected calls was made
        assert any(call in mock_import.call_args_list for call in expected_calls), f"Expected one of {expected_calls}, got {mock_import.call_args_list}"
    
    @patch('yaapp.discovery.importlib.import_module')
    def test_find_plugin_class_manager_suffix(self, mock_import):
        """Test finding plugin with Manager suffix."""
        # Mock module with StorageManager class
        mock_module = Mock()
        mock_class = Mock()
        mock_module.StorageManager = mock_class
        # No StoragePlugin
        del mock_module.StoragePlugin
        mock_import.return_value = mock_module
        
        result = self.discovery._find_plugin_class('storage')
        
        assert result == mock_class
        # The discovery system now tries .plugin first, then the direct module
        expected_calls = [
            call('yaapp.plugins.storage.plugin'),
            call('yaapp.plugins.storage')
        ]
        # Check that at least one of the expected calls was made
        assert any(call in mock_import.call_args_list for call in expected_calls), f"Expected one of {expected_calls}, got {mock_import.call_args_list}"
    
    @patch('yaapp.discovery.importlib.import_module')
    def test_find_plugin_class_title_case(self, mock_import):
        """Test finding plugin with title case class name."""
        # Mock module with Storage class
        mock_module = Mock()
        mock_class = Mock()
        mock_module.Storage = mock_class
        # No other classes
        del mock_module.StoragePlugin
        del mock_module.StorageManager
        mock_import.return_value = mock_module
        
        result = self.discovery._find_plugin_class('storage')
        
        assert result == mock_class
        # The discovery system now tries .plugin first, then the direct module
        expected_calls = [
            call('yaapp.plugins.storage.plugin'),
            call('yaapp.plugins.storage')
        ]
        # Check that at least one of the expected calls was made
        assert any(call in mock_import.call_args_list for call in expected_calls), f"Expected one of {expected_calls}, got {mock_import.call_args_list}"
    
    @patch('yaapp.discovery.importlib.import_module')
    def test_find_plugin_class_generic_plugin(self, mock_import):
        """Test finding plugin with generic Plugin class."""
        # Mock module with only Plugin class
        mock_module = Mock()
        mock_class = Mock()
        mock_module.Plugin = mock_class
        # No specific classes
        del mock_module.StoragePlugin
        del mock_module.StorageManager
        del mock_module.Storage
        mock_import.return_value = mock_module
        
        result = self.discovery._find_plugin_class('storage')
        
        assert result == mock_class
        # The discovery system now tries .plugin first, then the direct module
        expected_calls = [
            call('yaapp.plugins.storage.plugin'),
            call('yaapp.plugins.storage')
        ]
        # Check that at least one of the expected calls was made
        assert any(call in mock_import.call_args_list for call in expected_calls), f"Expected one of {expected_calls}, got {mock_import.call_args_list}"
    
    @patch('yaapp.discovery.importlib.import_module')
    def test_find_plugin_class_underscore_naming(self, mock_import):
        """Test finding plugin with underscore naming."""
        # Mock module - the discovery system will find Session_HandlerPlugin (with underscore)
        mock_module = Mock()
        mock_class = Mock()
        mock_module.Session_HandlerPlugin = mock_class
        mock_import.return_value = mock_module
        
        result = self.discovery._find_plugin_class('session_handler')
        
        # The discovery system finds Session_HandlerPlugin (title case with underscore)
        assert result == mock_module.Session_HandlerPlugin
        # The discovery system now tries .plugin first, then the direct module
        expected_calls = [
            call('yaapp.plugins.session_handler.plugin'),
            call('yaapp.plugins.session_handler')
        ]
        # Check that at least one of the expected calls was made
        assert any(call in mock_import.call_args_list for call in expected_calls), f"Expected one of {expected_calls}, got {mock_import.call_args_list}"
    
    @patch('yaapp.discovery.importlib.import_module')
    def test_find_plugin_class_hyphen_to_underscore(self, mock_import):
        """Test finding plugin with hyphen converted to underscore."""
        # First call fails (direct match)
        # Second call succeeds (hyphen to underscore)
        def side_effect(module_name):
            if module_name == 'yaapp.plugins.app-proxy':
                raise ImportError("No module named 'yaapp.plugins.app-proxy'")
            elif module_name == 'yaapp.plugins.app_proxy':
                mock_module = Mock()
                mock_class = Mock()
                mock_module.AppProxyPlugin = mock_class
                return mock_module
            else:
                raise ImportError(f"No module named '{module_name}'")
        
        mock_import.side_effect = side_effect
        
        result = self.discovery._find_plugin_class('app-proxy')
        
        assert result is not None
        # Should try both variations
        assert mock_import.call_count >= 2
    
    @patch('yaapp.discovery.importlib.import_module')
    def test_find_plugin_class_not_found(self, mock_import):
        """Test finding plugin that doesn't exist."""
        mock_import.side_effect = ImportError("No module found")
        
        result = self.discovery._find_plugin_class('nonexistent')
        
        assert result is None
    
    @patch('yaapp.discovery.importlib.import_module')
    def test_find_plugin_class_external_namespace(self, mock_import):
        """Test finding plugin in external namespace."""
        # First calls fail (yaapp.plugins)
        # Last call succeeds (yaapp_plugins)
        def side_effect(module_name):
            if module_name.startswith('yaapp.plugins.'):
                raise ImportError("No module in yaapp.plugins")
            elif module_name.startswith('yaapp_plugins.'):
                mock_module = Mock()
                mock_class = Mock()
                mock_module.CustomPlugin = mock_class
                return mock_module
            else:
                raise ImportError(f"No module named '{module_name}'")
        
        mock_import.side_effect = side_effect
        
        result = self.discovery._find_plugin_class('custom')
        
        assert result is not None
        # Should try external namespace
        assert any('yaapp_plugins.custom' in str(call) for call in mock_import.call_args_list)
    
    def test_try_load_plugin_class_names(self):
        """Test the class name patterns tried."""
        with patch('yaapp.discovery.importlib.import_module') as mock_import:
            mock_module = Mock()
            # Test that it tries multiple class names
            mock_module.StoragePlugin = Mock()
            mock_import.return_value = mock_module
            
            result = self.discovery._try_load_plugin('yaapp.plugins', 'storage', 'storage')
            
            assert result == mock_module.StoragePlugin
    
    def test_discover_plugins_integration(self):
        """Test discovering multiple plugins."""
        with patch.object(self.discovery, '_find_plugin_class') as mock_find:
            mock_storage = Mock()
            mock_routing = Mock()
            
            def side_effect(name):
                if name == 'storage':
                    return mock_storage
                elif name == 'routing':
                    return mock_routing
                return None
            
            mock_find.side_effect = side_effect
            
            result = self.discovery.discover_plugins(['storage', 'routing', 'nonexistent'])
            
            assert result == {
                'storage': mock_storage,
                'routing': mock_routing
            }
            assert 'nonexistent' not in result


if __name__ == '__main__':
    print("Test file - run manually")