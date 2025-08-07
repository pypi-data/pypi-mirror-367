"""
State plugin - abstraction layer on top of storage plugin.
Exposes storage interface methods with state management features.
"""

from typing import Any, Dict, List, Optional


class StateManager:
    """State management abstraction on top of storage plugin."""
    
    def __init__(self, app):
        """Initialize with app reference for calling storage functions."""
        self.app = app
    
    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Retrieve value by key from storage."""
        result = self.app.execute_function("storage.get", key=key, namespace=namespace)
        if result.is_ok():
            return result.unwrap()
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None, 
            namespace: str = "default") -> bool:
        """Store value in storage."""
        result = self.app.execute_function("storage.set", key=key, value=value, 
                                         ttl_seconds=ttl_seconds, namespace=namespace)
        return result.is_ok()
    
    def delete(self, key: str, namespace: str = "default") -> bool:
        """Delete value from storage."""
        result = self.app.execute_function("storage.delete", key=key, namespace=namespace)
        return result.is_ok()
    
    def exists(self, key: str, namespace: str = "default") -> bool:
        """Check if key exists in storage."""
        result = self.app.execute_function("storage.exists", key=key, namespace=namespace)
        if result.is_ok():
            return result.unwrap()
        return False
    
    def keys(self, pattern: Optional[str] = None, namespace: str = "default") -> List[str]:
        """List keys from storage."""
        result = self.app.execute_function("storage.keys", pattern=pattern, namespace=namespace)
        if result.is_ok():
            return result.unwrap()
        return []
    
    def clear(self, namespace: str = "default") -> int:
        """Clear data from storage namespace."""
        result = self.app.execute_function("storage.clear", namespace=namespace)
        if result.is_ok():
            return result.unwrap()
        return 0