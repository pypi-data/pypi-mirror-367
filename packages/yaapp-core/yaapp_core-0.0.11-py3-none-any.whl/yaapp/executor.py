"""
Executor for yaapp - ASYNC-FIRST execution logic extracted from core.

This handles all execution logic with async flow, keeping it separate from 
storage (registry) and orchestration (core).

IMPORTANT: All execution flow is ASYNC-FIRST!
- Primary method: execute() is async
- Uses exposer.run_async() for async execution
- Sync wrapper available for backward compatibility

Replaces: core._execute_from_registry() with async-first approach
"""

import asyncio
from typing import Any
from .result import Result, Ok


class Executor:
    """ASYNC-FIRST Executor that handles function execution using registry and exposers.
    
    Responsibilities:
    - Get (object, exposer) from registry
    - Use exposer.run_async() for ASYNC execution
    - Handle execution errors
    - Return Result objects
    
    ASYNC-FIRST DESIGN:
    - execute() is async - primary method
    - execute_sync() is sync wrapper for backward compatibility
    
    Used by:
    - YaappEngine: execute() delegates to executor.execute() [ASYNC]
    - Click runner: CLI execution delegates to executor.execute() [ASYNC]
    """
    
    def __init__(self, registry):
        """Initialize executor with registry instance.
        
        Args:
            registry: Registry instance to use for command lookup
        """
        self.registry = registry
    
    async def execute(self, name: str, **kwargs) -> Result[Any]:
        """ASYNC-FIRST execution from registry using exposer.run_async().
        
        Args:
            name: Name of function in registry
            **kwargs: Arguments to pass to function
            
        Returns:
            Result containing function result or error
            
        ASYNC FLOW:
        1. Get (object, exposer) from registry
        2. Use exposer.run_async() - ALWAYS ASYNC
        3. Exposer handles sync functions via thread pools
        4. Return Result
        
        Replaces: core._execute_from_registry() with async-first approach
        """
        # Get (object, exposer) from registry
        result = self.registry.get_both(name)
        if result.is_err():
            return result
        
        obj, exposer = result.unwrap()
        
        # Use exposer to execute the function - ASYNC FIRST
        if hasattr(exposer, "run_async"):
            # ASYNC execution - primary path
            result = await exposer.run_async(obj, **kwargs)
            if hasattr(result, "is_ok") and hasattr(result, "unwrap"):
                # It's already a Result object
                return result
            else:
                # Wrap result in Ok
                return Ok(result)
        elif hasattr(exposer, "run"):
            # Fallback to sync exposer.run() - wrap in thread pool
            try:
                loop = asyncio.get_event_loop()
            except (RuntimeError, OSError) as e:
                return Result.error(f"Failed to get event loop for sync execution: {str(e)}")
            
            try:
                result = await loop.run_in_executor(None, lambda: exposer.run(obj, **kwargs))
                if hasattr(result, "is_ok") and hasattr(result, "unwrap"):
                    return result
                else:
                    return Ok(result)
            except (RuntimeError, OSError, AttributeError, asyncio.InvalidTaskError, asyncio.CancelledError) as e:
                # Protect against asyncio event loop issues (foreign library)
                return Result.error(f"Sync execution failed: {str(e)}")
        else:
            # Fallback to direct execution - wrap in thread pool
            try:
                loop = asyncio.get_event_loop()
            except (RuntimeError, OSError) as e:
                return Result.error(f"Failed to get event loop for direct execution: {str(e)}")
            
            try:
                result = await loop.run_in_executor(None, lambda: obj(**kwargs))
                return Ok(result)
            except (RuntimeError, OSError, AttributeError, asyncio.InvalidTaskError, asyncio.CancelledError) as e:
                # Protect against asyncio event loop issues (foreign library)
                return Result.error(f"Direct execution failed: {str(e)}")
    
    def execute_sync(self, name: str, **kwargs) -> Result[Any]:
        """Sync wrapper for backward compatibility.
        
        Args:
            name: Name of function in registry
            **kwargs: Arguments to pass to function
            
        Returns:
            Result containing function result or error
            
        This is just a sync wrapper around the async execute() method.
        Use execute() directly for async contexts.
        """
        return asyncio.run(self.execute(name, **kwargs))


# No singleton - each YaappEngine creates its own Executor instance
