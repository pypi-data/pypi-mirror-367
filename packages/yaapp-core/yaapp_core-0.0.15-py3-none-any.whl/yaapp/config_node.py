"""
Hierarchical configuration node with automatic inheritance.
"""

from typing import Any, Optional
from .result import Result, Ok


class ConfigNode:
    """
    Hierarchical configuration node with automatic inheritance.
    
    Each node can:
    1. Look in its own data
    2. Ask parent for missing values
    3. Auto-instantiate child nodes
    4. Prevent infinite loops
    """
    
    def __init__(self, data: dict, parent: 'ConfigNode' = None, path: str = ""):
        self._data = data or {}
        self._parent = parent
        self._path = path
        self._children = {}
    
    def get_attr(self, key: str) -> Result[Any]:
        """Get attribute with inheritance - Result[T] compliant replacement for __getattr__.
        
        Args:
            key: The attribute/key to access
            
        Returns:
            Result[Any]: Ok with the value if found, Err if the key is invalid
        """
        # Avoid recursion for internal attributes
        if key.startswith('_'):
            return Result.error(f"'{self.__class__.__name__}' object has no attribute '{key}'")
        
        current_path = f"{self._path}.{key}" if self._path else key
        
        # Step 1: Check our own data
        if key in self._data:
            value = self._data[key]
            if isinstance(value, dict):
                # Create child config node with inheritance
                if key not in self._children:
                    # Get parent data for this key to merge
                    parent_data = {}
                    if self._parent:
                        parent_result = self._parent.get_attr(key)
                        if parent_result.is_ok():
                            parent_value = parent_result.unwrap()
                            if isinstance(parent_value, ConfigNode):
                                parent_data = parent_value._data
                            elif isinstance(parent_value, dict):
                                parent_data = parent_value
                    
                    # Merge parent data with our data (our data takes precedence)
                    merged_data = {**parent_data, **value}
                    self._children[key] = ConfigNode(merged_data, parent=self, path=current_path)
                return Ok(self._children[key])
            return Ok(value)
        
        # Step 2: Ask parent for the key (inheritance)
        if self._parent:
            parent_result = self._parent.get_attr(key)
            if parent_result.is_ok():
                parent_value = parent_result.unwrap()
                if isinstance(parent_value, ConfigNode):
                    # Create a copy with updated path
                    if key not in self._children:
                        self._children[key] = ConfigNode(parent_value._data, parent=self, path=current_path)
                    return Ok(self._children[key])
                else:
                    return Ok(parent_value)
        
        # Step 3: Create empty child node (auto-instantiation)
        if key not in self._children:
            self._children[key] = ConfigNode({}, parent=self, path=current_path)
        return Ok(self._children[key])
    
    def _get_by_path(self, path: str):
        """Get value by full dot notation path."""
        parts = path.split('.')
        current = self._data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        if isinstance(current, dict):
            return ConfigNode(current, parent=self, path=path)
        return current
    

    
    def get(self, key: str, default=None):
        """Safe get with default value."""
        result = self.get_attr(key)
        if result.is_ok():
            value = result.unwrap()
            # Check if it's an empty auto-instantiated node
            if isinstance(value, ConfigNode) and not value._data:
                return default
            return value
        else:
            return default
    
    def __bool__(self):
        """Return True if node has data."""
        return bool(self._data)
    
    def __repr__(self):
        """String representation for debugging."""
        return f"ConfigNode(path='{self._path}', data={self._data})"
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self._data.copy()