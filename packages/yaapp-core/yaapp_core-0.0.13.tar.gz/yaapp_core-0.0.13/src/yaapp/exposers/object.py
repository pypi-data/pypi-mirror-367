"""
Object exposer for object instances.
"""
import inspect
from typing import Any, Dict

from ..result import Result, Ok
from .utils import _reflect_class_commands
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
            "commands": _reflect_class_commands(cls)
        }
        return Ok(metadata)

    async def run(self, instance: object, subcommand_name: str, **kwargs) -> Result[Any]:
        """Run a subcommand on the object instance.
        
        Args:
            instance: Object instance to call subcommand on
            subcommand_name: Name of subcommand to call
            **kwargs: Additional arguments to pass to subcommand
        """
        if not hasattr(instance, subcommand_name):
            return Result.error(f"Object has no subcommand '{subcommand_name}'")

        method = getattr(instance, subcommand_name)
        if not callable(method):
            return Result.error(f"Attribute '{subcommand_name}' is not callable")

        return await smart_call_async(method, **kwargs)
    
    # Backward compatibility method
    async def run_method(self, instance: object, method_name: str, **kwargs) -> Result[Any]:
        """Run a method on the object instance.
        
        DEPRECATED: Use run() with subcommand_name parameter instead.
        """
        return await self.run(instance, method_name, **kwargs)
