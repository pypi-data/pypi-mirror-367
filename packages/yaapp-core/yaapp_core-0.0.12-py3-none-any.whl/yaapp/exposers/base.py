"""
Base exposer class for the yaapp exposer system.
"""

from abc import ABC, abstractmethod
from typing import Any
from ..result import Result


class BaseExposer(ABC):
    """Base class for all exposers."""
    
    def expose(self, item: Any, name: str, custom: bool = False) -> Result[bool]:
        """Default expose method - just validates the item type."""
        return Result.ok(True)
    
    @abstractmethod
    def run(self, item: Any, **kwargs) -> Result[Any]:
        """Run the item with given arguments (sync context)."""
        pass
    
    async def run_async(self, item: Any, **kwargs) -> Result[Any]:
        """Run the item with given arguments (async context) - default to sync."""
        return self.run(item, **kwargs)