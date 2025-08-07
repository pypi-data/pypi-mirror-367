"""
Test Storage Plugin yaapp Integration

Test that storage plugin works with the new discovery system.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp import Yaapp
from yaapp.plugins.storage.plugin import Storage


def test_storage_class_can_be_exposed():
    """Test that Storage class can be exposed to yaapp."""
    # Create fresh app instance for testing
    app = Yaapp(auto_discover=False)
    
    # Expose Storage manually
    app.expose(Storage)
    
    registry = app.get_registry_items()
    assert 'Storage' in registry
    
    storage_class = registry['Storage']
    assert storage_class is Storage


def test_storage_instance_functionality():
    """Test that Storage instance works correctly."""
    # Create instance with memory backend
    config = {'backend': 'memory'}
    storage = Storage(config)
    
    # Test basic operations
    assert storage.set("test", "hello") == True
    assert storage.get("test") == "hello"
    assert storage.exists("test") == True
    assert "test" in storage.keys()
    assert storage.delete("test") == True
    assert storage.get("test") is None


def test_storage_with_yaapp_integration():
    """Test storage plugin with yaapp integration."""
    # Create fresh app instance
    app = Yaapp(auto_discover=False)
    
    # Create and expose storage instance
    config = {'backend': 'memory'}
    storage = Storage(config)
    app.expose(storage, name='storage')
    
    # Test through registry
    registry = app.get_registry_items()
    assert 'storage' in registry
    
    storage_instance = registry['storage']
    assert storage_instance.set("integration_test", "success") == True
    assert storage_instance.get("integration_test") == "success"


if __name__ == "__main__":
    test_storage_class_can_be_exposed()
    print("✅ Storage class exposure test passed")
    
    test_storage_instance_functionality()
    print("✅ Storage instance functionality test passed")
    
    test_storage_with_yaapp_integration()
    print("✅ Storage yaapp integration test passed")
    
    print("🎉 All storage integration tests passed!")