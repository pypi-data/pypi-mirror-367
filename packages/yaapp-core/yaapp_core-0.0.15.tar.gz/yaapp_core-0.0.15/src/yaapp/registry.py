"""
Registry for yaapp - extracted from core boilerplate.

This is the lowest level component that stores (object, exposer) pairs.
Each YaappEngine creates its own Registry instance for complete isolation.

Replaces scattered boilerplate from core.py:
- self._registry: Dict[str, Tuple[Any, BaseExposer]] = {}
- get_registry_item(), get_registry_exposer(), get_registry_items()
- _execute_from_registry()
"""

from typing import Any, Dict, Tuple, Optional
from .result import Result, Ok


class Registry:
    """Registry that stores (object, exposer) pairs.
    
    Each YaappEngine instance creates its own Registry for complete isolation.
    This ensures that different Yaapp() instances don't interfere with each other.
    
    Used by:
    - YaappEngine: To store and retrieve exposed objects
    - Executor: To get objects for execution
    - expose.py: To register @expose decorated functions/classes
    - Click runner: To build CLI commands from registered items
    """
    
    def __init__(self):
        self._items: Dict[str, Tuple[Any, Any]] = {}  # {name: (obj, exposer)}
    
    def add(self, name: str, obj: Any, exposer: Any) -> None:
        """Add an object with its exposer to the registry.
        
        Args:
            name: Unique name for the object (e.g., "calculator", "test")
            obj: The actual object (function, class instance, etc.)
            exposer: The exposer that knows how to run this object
                    (FunctionExposer, ClassExposer, ObjectExposer, CustomExposer)
        
        Replaces: self._registry[name] = (registry_obj, exposer)
        """
        self._items[name] = (obj, exposer)
    
    def exists(self, name: str) -> bool:
        """Check if name exists in registry.
        
        Args:
            name: Name to check
            
        Returns:
            True if name is registered, False otherwise
            
        Replaces: name in self._registry
        """
        return name in self._items
    
    def get_item(self, name: str) -> Result[Any]:
        """Get raw object from registry.
        
        Args:
            name: Name of item in registry
            
        Returns:
            Result containing raw object from registry or error
            
        Used by:
        - app.py: get_registry_item() to check if function exists
        - config.py: get_registry_item() to verify plugin registration
        
        Replaces: core.get_registry_item()
        """
        if name not in self._items:
            return Result.error(f"Item '{name}' not found in registry")
        obj, exposer = self._items[name]
        return Ok(obj)
    
    def get_exposer(self, name: str) -> Result[Any]:
        """Get exposer for item from registry.
        
        Args:
            name: Name of item in registry
            
        Returns:
            Result containing exposer object from registry or error
            
        The exposer knows how to validate and execute the object:
        - FunctionExposer: for functions
        - ClassExposer: for classes (creates instances)
        - ObjectExposer: for object instances
        - CustomExposer: for custom objects
        
        Replaces: core.get_registry_exposer()
        """
        if name not in self._items:
            return Result.error(f"Item '{name}' not found in registry")
        obj, exposer = self._items[name]
        return Ok(exposer)
    
    def get_both(self, name: str) -> Result[Tuple[Any, Any]]:
        """Get both object and exposer from registry.
        
        Args:
            name: Name of item in registry
            
        Returns:
            Result containing (object, exposer) tuple or error
            
        Used internally by execute() method.
        """
        if name not in self._items:
            return Result.error(f"Function '{name}' not found")
        return Ok(self._items[name])
    

    
    def list_items(self) -> Dict[str, Tuple[Any, Any]]:
        """Get all items from registry (name -> (metadata, exposer))."""
        return self._items
    
    def list_names(self) -> list:
        """Get all registered names.
        
        Returns:
            List of all registered names
            
        Useful for debugging and introspection.
        """
        return list(self._items.keys())
    
    def remove(self, name: str) -> bool:
        """Remove item from registry.
        
        Args:
            name: Name of item to remove
            
        Returns:
            True if item was removed, False if not found
            
        Useful for dynamic plugin unloading.
        """
        if name in self._items:
            del self._items[name]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all items from registry.
        
        Useful for testing and cleanup.
        """
        self._items.clear()


# No singleton - each YaappEngine creates its own Registry instance