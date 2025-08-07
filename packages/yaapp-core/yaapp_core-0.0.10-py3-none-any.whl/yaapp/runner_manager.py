"""
RunnerManager - Handles polymorphic runner execution.

Supports both string runner names and custom runner objects.
Delegates to appropriate runner without Yaapp knowing about Click.
"""

from typing import Union, Any, Optional
from .yaapp_engine import YaappEngine
from .result import Result, Ok


class RunnerManager:
    """Manages runner execution - polymorphic string or object."""
    
    def __init__(self, yaapp_engine: YaappEngine):
        """Initialize with yaapp engine reference."""
        self.yaapp_engine = yaapp_engine
        self._default_runner = "click"
    
    def run(self, runner: Union[str, Any, None] = None, **kwargs) -> Result[None]:
        """Run with specified runner (polymorphic).
        
        Args:
            runner: Can be:
                - None: Use default runner (click)
                - str: Load runner by name from runners/ directory
                - object: Custom runner instance
            **kwargs: Arguments to pass to runner
            
        Returns:
            Result[None]: Ok(None) if successful, Err with error message if failed
        """
        if runner is None:
            # Use default runner
            return self._run_by_name(self._default_runner, **kwargs)
        elif isinstance(runner, str):
            # Load runner by name
            return self._run_by_name(runner, **kwargs)
        else:
            # Custom runner object
            return self._run_custom_runner(runner, **kwargs)
    
    def _run_by_name(self, runner_name: str, **kwargs) -> Result[None]:
        """Load and run runner by name.
        
        Returns:
            Result[None]: Ok(None) if successful, Err with error message if failed
        """
        # Get runner module from cache
        runner_module = self.yaapp_engine.get_runner_module(runner_name)
        
        if runner_module is None:
            return Result.error(f"Runner '{runner_name}' not found")
        
        # Call run() function directly on module
        if hasattr(runner_module, 'run') and callable(getattr(runner_module, 'run')):
            runner_module.run(self.yaapp_engine, **kwargs)
            return Ok(None)
        else:
            return Result.error(f"Runner '{runner_name}' module does not have run() function")
    
    def _run_custom_runner(self, runner: Any, **kwargs) -> Result[None]:
        """Run custom runner object.
        
        Returns:
            Result[None]: Ok(None) if successful, Err with error message if failed
        """
        if not hasattr(runner, 'run'):
            return Result.error(f"Runner {runner} must have run() method")
        
        # Call runner with yaapp_engine
        runner.run(self.yaapp_engine, **kwargs)
        return Ok(None)
    
    def set_default_runner(self, runner_name: str) -> None:
        """Set default runner name."""
        self._default_runner = runner_name
    
    def get_available_runners(self) -> list:
        """Get list of available runner names (triggers lazy discovery)."""
        return list(self.yaapp_engine.get_runners().keys())