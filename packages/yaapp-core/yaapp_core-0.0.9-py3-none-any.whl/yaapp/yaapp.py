"""
Yaapp - Main library interface.

Clean library API that doesn't import Click or any specific runners.
Delegates to YaappEngine and RunnerManager for actual work.
"""

from typing import Any, Optional, Union

from .result import Result
from .yaapp_engine import YaappEngine


class Yaapp:
    """Main library interface - clean and simple.

    Usage:
        from yaapp import Yaapp

        yaapp = Yaapp()
        yaapp.add_plugin(my_plugin)
        yaapp.run("fastapi")  # or yaapp.run(my_runner)
    """

    def __init__(self):
        """Initialize Yaapp library - creates its own YaappEngine instance.

        NOTE: Constructor is lightweight - no I/O operations!
        Call activate() for full initialization with config loading.
        """
        self.engine = YaappEngine()  # ← Each Yaapp creates its own engine

    async def activate(self) -> Result[bool]:
        """Activate the Yaapp instance - load config and plugins asynchronously.

        Returns:
            Result[bool]: Success/failure of activation
        """
        return await self.engine.activate()

    def run(self, runner: Union[str, Any, None] = None, **kwargs) -> None:
        """Run with specified runner (polymorphic).

        Args:
            runner: Can be:
                - None: Use default runner (click)
                - str: Runner name ("click", "fastapi", "prompt", etc.)
                - object: Custom runner instance
            **kwargs: Arguments to pass to runner
        """
        # Engine handles lazy activation and error reporting internally
        self.engine.run(runner=runner, **kwargs)

    def add_plugin(self, plugin: Any, name: Optional[str] = None) -> None:
        """Add a plugin to the system.

        Args:
            plugin: Plugin instance
            name: Optional name (defaults to plugin class name)
        """
        plugin_name = name or plugin.__class__.__name__.lower()
        self.engine.register_plugin(plugin_name, plugin)
        # Don't run plugin here - only when app runs

    

    def expose(self, obj: Any, name: Optional[str] = None, **kwargs) -> None:
        """Expose an object to the system.

        Args:
            obj: Object to expose (function, class, etc.)
            name: Optional name
            **kwargs: Additional exposure options
        """
        self.engine.expose(obj, name, **kwargs)

    # ===== QUERY API =====
    def get_commands(self) -> dict:
        """Get available commands."""
        return self.engine.get_commands()

    def get_plugins(self) -> dict:
        """Get registered plugins."""
        return self.engine.get_plugins()

    def get_runners(self) -> dict:
        """Get available runners."""
        return self.engine.get_runners()
