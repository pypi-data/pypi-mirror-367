"""
Unit tests for the yaapp singleton instance.
Tests that the singleton works correctly and auto-discovery functions.
"""

# import pytest  # Not needed for simple tests
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestSingletonInstance:
    """Test the yaapp singleton instance."""
    
    def test_singleton_import(self):
        """Test that yaapp singleton can be imported."""
        # Import the singleton
        from yaapp import yaapp
        
        # Should be a Yaapp instance
        from yaapp import Yaapp
        assert isinstance(yaapp, Yaapp)
    
    def test_singleton_is_same_instance(self):
        """Test that multiple imports return the same instance."""
        # Import twice
        from yaapp import yaapp as yaapp1
        from yaapp import yaapp as yaapp2
        
        # Should be the same object
        assert yaapp1 is yaapp2
    
    def test_singleton_vs_class_import(self):
        """Test that both singleton and class are available."""
        from yaapp import yaapp, Yaapp
        
        # yaapp should be instance, Yaapp should be class
        assert isinstance(yaapp, Yaapp)
        assert yaapp.__class__ is Yaapp
    
    def test_singleton_has_auto_discovery(self):
        """Test that singleton has auto-discovery enabled by default."""
        # Create fresh instance to test auto_discover parameter
        from yaapp import Yaapp
        
        # Default should have auto_discover=True
        with patch.object(Yaapp, '_auto_discover_plugins') as mock_discover:
            app = Yaapp()
            mock_discover.assert_called_once()
    
    def test_singleton_can_disable_auto_discovery(self):
        """Test that auto-discovery can be disabled."""
        from yaapp import Yaapp
        
        # Should be able to disable auto_discover
        with patch.object(Yaapp, '_auto_discover_plugins') as mock_discover:
            app = Yaapp(auto_discover=False)
            mock_discover.assert_not_called()
    
    @patch('yaapp.app.Yaapp._load_config')
    def test_auto_discover_plugins_calls_config(self, mock_load_config):
        """Test that auto_discover_plugins loads config."""
        from yaapp import Yaapp
        
        # Mock config with register method
        mock_config = Mock()
        mock_config.register_discovered_plugins = Mock()
        mock_load_config.return_value = mock_config
        
        # Create instance (triggers auto-discovery)
        app = Yaapp()
        
        # Should load config and register plugins
        mock_load_config.assert_called()
        mock_config.register_discovered_plugins.assert_called_with(app)
    
    @patch('yaapp.app.Yaapp._load_config')
    def test_auto_discover_plugins_handles_errors(self, mock_load_config):
        """Test that auto_discover_plugins handles errors gracefully."""
        from yaapp import Yaapp
        
        # Mock config loading to raise error
        mock_load_config.side_effect = Exception("Config error")
        
        # Should not raise exception
        with patch('builtins.print') as mock_print:
            app = Yaapp()
            
            # Should print warning
            mock_print.assert_called()
            warning_call = mock_print.call_args_list[-1]
            assert "Warning: Failed to auto-discover plugins" in str(warning_call)
    
    def test_singleton_registry_starts_empty(self):
        """Test that singleton starts with empty registry."""
        # Import fresh singleton (in test environment)
        from yaapp import Yaapp
        
        # Create test instance
        app = Yaapp(auto_discover=False)
        
        # Registry should start empty
        assert app.get_registry_items() == {}
    
    def test_singleton_can_expose_functions(self):
        """Test that singleton can expose functions normally."""
        from yaapp import Yaapp
        
        # Create test instance
        app = Yaapp(auto_discover=False)
        
        # Expose a test function
        @app.expose
        def test_function():
            return "test result"
        
        # Should be in registry
        registry = app.get_registry_items()
        assert 'test_function' in registry
        assert registry['test_function'] == test_function


class TestSingletonIntegration:
    """Integration tests for singleton with discovery system."""
    
    @patch('yaapp.config.YaappConfig.load')
    def test_singleton_with_mock_config(self, mock_config_load):
        """Test singleton with mocked configuration."""
        from yaapp import Yaapp
        
        # Mock config with plugins
        mock_config = Mock()
        mock_config.register_discovered_plugins = Mock()
        mock_config_load.return_value = mock_config
        
        # Create instance
        app = Yaapp()
        
        # Should call config methods
        mock_config_load.assert_called()
        mock_config.register_discovered_plugins.assert_called_with(app)
    
    def test_singleton_expose_and_registry(self):
        """Test that singleton expose and registry work together."""
        from yaapp import Yaapp
        
        # Create test instance
        app = Yaapp(auto_discover=False)
        
        # Expose multiple items
        @app.expose
        def func1():
            return 1
        
        @app.expose
        def func2():
            return 2
        
        class TestClass:
            def method(self):
                return "method"
        
        app.expose(TestClass)
        
        # Check registry
        registry = app.get_registry_items()
        assert 'func1' in registry
        assert 'func2' in registry
        assert 'TestClass' in registry
        
        assert len(registry) == 3


if __name__ == '__main__':
    # Simple test runner without pytest
    print("Running singleton instance tests...")
    
    # Run TestSingletonInstance tests
    test_instance = TestSingletonInstance()
    test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
    
    passed = 0
    failed = 0
    
    for method_name in test_methods:
        try:
            print(f"Running {method_name}...", end=" ")
            method = getattr(test_instance, method_name)
            method()
            print("✅ PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
            failed += 1
    
    # Run TestSingletonIntegration tests
    integration_instance = TestSingletonIntegration()
    integration_methods = [method for method in dir(integration_instance) if method.startswith('test_')]
    
    for method_name in integration_methods:
        try:
            print(f"Running {method_name}...", end=" ")
            method = getattr(integration_instance, method_name)
            method()
            print("✅ PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    if failed == 0:
        print("🎉 All singleton tests passed!")
    else:
        print("💥 Some singleton tests failed!")
        sys.exit(1)