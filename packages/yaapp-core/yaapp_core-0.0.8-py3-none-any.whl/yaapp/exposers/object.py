"""
Object exposer for object instances.
"""
import inspect
from typing import Any, Dict

from ..result import Result, Ok
from .utils import _reflect_class_methods
from ..async_compat import smart_call_async

class ObjectExposer:
    """Exposer for object instances."""

    def get_metadata(self, instance: object) -> Result[Dict[str, Any]]:
        """Get metadata for the exposed object instance."""
        if inspect.isclass(instance) or (callable(instance) and not hasattr(instance, '__self__')):
            return Result.error(f"ObjectExposer cannot expose {type(instance)}")

        cls = type(instance)
        docstring = inspect.getdoc(cls) or "No description."
        short_doc = docstring.split('\n')[0]

        metadata = {
            "name": cls.__name__,
            "type": "group",
            "help": short_doc,
            "commands": _reflect_class_methods(cls)
        }
        return Ok(metadata)

    async def run(self, instance: object, method_name: str, yaapp_engine=None, **kwargs) -> Result[Any]:
        """Run a method on the object instance.
        
        Args:
            instance: Object instance to call method on
            method_name: Name of method to call
            yaapp_engine: YaappEngine instance to inject as first parameter (if method expects it)
            **kwargs: Additional arguments to pass to method
        """
        if not hasattr(instance, method_name):
            return Result.error(f"Object has no method '{method_name}'")

        method = getattr(instance, method_name)
        if not callable(method):
            return Result.error(f"Attribute '{method_name}' is not callable")

        # Check if method expects yaapp_engine as first parameter (after self)
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        
        # Skip 'self' parameter and check if next parameter is 'yaapp_engine'
        if len(params) > 1 and params[1] == 'yaapp_engine' and yaapp_engine is not None:
            kwargs = {'yaapp_engine': yaapp_engine, **kwargs}

        return await smart_call_async(method, **kwargs)
