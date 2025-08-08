"""
Class exposer for class introspection and method exposure.
"""
import inspect
from typing import Any, Dict
import asyncio

from ..result import Result, Ok
from .utils import _reflect_class_commands

class ClassExposer:
    """Exposer for classes. Caches instances and provides metadata."""

    def __init__(self):
        """Initialize class exposer with instance cache."""
        self._instance_cache: Dict[type, Any] = {}

    def get_metadata(self, cls: type) -> Result[Dict[str, Any]]:
        """Get metadata for the exposed class."""
        if not inspect.isclass(cls):
            return Result.error(f"ClassExposer cannot expose {type(cls)}: {cls}")

        docstring = inspect.getdoc(cls) or "No description."
        short_doc = docstring.split('\n')[0]

        metadata = {
            "name": cls.__name__,
            "type": "group",
            "help": short_doc,
            "commands": _reflect_class_commands(cls)
        }
        return Ok(metadata)

    async def run(self, cls: type, yaapp_engine=None, **kwargs) -> Result[Any]:
        """Run method: for a class, this means creating and returning an instance."""
        if not inspect.isclass(cls):
            return Result.error(f"Cannot run a non-class item: {cls}")

        try:
            if cls not in self._instance_cache:
                # Check if constructor actually accepts yaapp_engine parameter
                sig = inspect.signature(cls.__init__)
                params = list(sig.parameters.keys())
                
                # Skip 'self' parameter and check if next parameter is 'yaapp_engine'
                # Only inject if constructor explicitly expects it
                if len(params) > 1 and params[1] == 'yaapp_engine' and yaapp_engine is not None:
                    self._instance_cache[cls] = cls(yaapp_engine)
                else:
                    # Constructor doesn't expect yaapp_engine, create normally
                    self._instance_cache[cls] = cls()
            # Yield control to event loop, then return the cached instance
            await asyncio.sleep(0)
            return Ok(self._instance_cache[cls])
        except (TypeError, ValueError, AttributeError, asyncio.InvalidStateError, asyncio.CancelledError) as e:
            return Result.error(f"Failed to instantiate class {cls}: {str(e)}")
