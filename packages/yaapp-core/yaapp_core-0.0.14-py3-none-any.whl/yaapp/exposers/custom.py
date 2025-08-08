"""
Custom exposer for objects that implement their own exposure logic.
"""

import inspect
from typing import Any, Dict, Optional

from ..result import Result, Ok
from ..async_compat import smart_call_async
from .utils import _reflect_function, _reflect_class_commands

class CustomExposer:
    """Exposer for custom objects that handle their own exposure and execution."""

    def get_metadata(self, item: Any) -> Result[Dict[str, Any]]:
        """Get metadata for the exposed custom object."""
        if inspect.isclass(item):
            # If it's a class, check if it provides its own metadata
            if hasattr(item, 'get_exposed_metadata') and callable(item.get_exposed_metadata):
                try:
                    # Custom class provides its own metadata
                    metadata = item.get_exposed_metadata()
                    if not isinstance(metadata, dict):
                        return Result.error("Custom object's get_exposed_metadata must return a dict")
                    # Ensure consistency: if custom metadata uses 'methods', rename to 'subcommands'
                    if "methods" in metadata:
                        metadata["commands"] = metadata.pop("methods")
                    return Ok(metadata)
                except (AttributeError, TypeError) as e:
                    return Result.error(f"Error getting custom metadata from class {item.__name__}: {e}")
            elif hasattr(item, 'execute_call') and callable(item.execute_call):
                # If it only has execute_call, treat it as a single command
                metadata = _reflect_function(item.execute_call)
                metadata["name"] = item.__name__
                metadata["type"] = "command"
                return Ok(metadata)
            else:
                return Result.error(f"Custom class {item.__name__} must implement get_exposed_metadata() or execute_call()")
        elif hasattr(item, 'execute_call') and callable(item.execute_call):
            # If it's an instance with execute_call, treat as a single command
            metadata = _reflect_function(item.execute_call)
            metadata["name"] = item.__class__.__name__ # Use class name for instance
            metadata["type"] = "command"
            return Ok(metadata)
        elif hasattr(item, 'get_exposed_metadata') and callable(item.get_exposed_metadata):
            # If it's an instance with get_exposed_metadata
            try:
                metadata = item.get_exposed_metadata()
                if not isinstance(metadata, dict):
                    return Result.error("Custom object's get_exposed_metadata must return a dict")
                return Ok(metadata)
            except (AttributeError, TypeError) as e:
                return Result.error(f"Error getting custom metadata from instance {item.__class__.__name__}: {e}")
        else:
            return Result.error(f"Custom object {item} must implement get_exposed_metadata() or execute_call()")

    async def run(self, item: Any, method_name: Optional[str] = None, yaapp_engine=None, **kwargs) -> Result[Any]:
        """Run the custom object's logic.
        
        Args:
            item: Custom object to execute
            method_name: Optional method name to call
            yaapp_engine: YaappEngine instance to inject as first parameter (if method expects it)
            **kwargs: Additional arguments to pass to method
        """
        target_callable: Any

        if inspect.isclass(item):
            try:
                instance = item() # Instantiate the custom class
            except (TypeError, ValueError) as e:
                return Result.error(f"Failed to instantiate custom class {item.__name__}: {e}")
            
            if method_name:
                if not hasattr(instance, method_name) or not callable(getattr(instance, method_name)):
                    return Result.error(f"Custom class instance has no callable method '{method_name}'")
                target_callable = getattr(instance, method_name)
            elif hasattr(instance, 'execute_call') and callable(instance.execute_call):
                target_callable = instance.execute_call
            else:
                return Result.error(f"Custom class instance {item.__name__} must have execute_call() or specified method_name")
        else: # It's an instance
            if method_name:
                if not hasattr(item, method_name) or not callable(getattr(item, method_name)):
                    return Result.error(f"Custom object has no callable method '{method_name}'")
                target_callable = getattr(item, method_name)
            elif hasattr(item, 'execute_call') and callable(item.execute_call):
                target_callable = item.execute_call
            else:
                return Result.error(f"Custom object {item.__class__.__name__} must have execute_call() or specified method_name")

        # Check if target callable expects yaapp_engine parameter
        sig = inspect.signature(target_callable)
        params = list(sig.parameters.keys())
        
        # For methods, skip 'self' parameter and check if next parameter is 'yaapp_engine'
        # For functions, check if first parameter is 'yaapp_engine'
        if hasattr(target_callable, '__self__'):  # It's a bound method
            if len(params) > 1 and params[1] == 'yaapp_engine' and yaapp_engine is not None:
                kwargs = {'yaapp_engine': yaapp_engine, **kwargs}
        else:  # It's a function
            if params and params[0] == 'yaapp_engine' and yaapp_engine is not None:
                kwargs = {'yaapp_engine': yaapp_engine, **kwargs}

        return await smart_call_async(target_callable, **kwargs)
