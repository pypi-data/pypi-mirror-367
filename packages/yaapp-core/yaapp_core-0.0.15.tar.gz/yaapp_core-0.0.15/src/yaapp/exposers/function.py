"""
Function exposer for regular functions with async/sync support.
"""
import asyncio
import inspect
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Any, Dict

from ..result import Result, Ok
from .utils import _reflect_function
from ..async_compat import smart_call_async
from ..execution_strategy import (
    get_execution_hint,
    should_use_thread_pool,
    should_use_process_pool
)

class FunctionExposer:
    """Exposer for standalone functions. Manages execution strategies."""

    def __init__(self, max_workers: int = 4):
        """Initialize function exposer with thread and process pools."""
        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self._process_pool: ProcessPoolExecutor | None = None

    def get_metadata(self, func: callable) -> Result[Dict[str, Any]]:
        """Get metadata for the exposed function."""
        if not callable(func) or inspect.isclass(func):
            return Result.error(f"FunctionExposer cannot expose {type(func)}")

        metadata = _reflect_function(func)
        metadata["name"] = func.__name__
        return Ok(metadata)

    async def run(self, func: callable, yaapp_engine=None, **kwargs) -> Result[Any]:
        """Run the function with given arguments using execution strategies.
        
        Args:
            func: Function to execute
            yaapp_engine: YaappEngine instance to inject as first parameter (if function expects it)
            **kwargs: Additional arguments to pass to function
        """
        if not callable(func):
            return Result.error(f"Cannot run non-callable item: {func}")

        # Check if function expects yaapp_engine as first parameter
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        
        # If function expects yaapp_engine as first parameter, inject it
        if params and params[0] == 'yaapp_engine' and yaapp_engine is not None:
            kwargs = {'yaapp_engine': yaapp_engine, **kwargs}

        execution_hint = get_execution_hint(func)

        if should_use_process_pool(func, execution_hint):
            return await self._run_in_process_pool(func, **kwargs)
        elif should_use_thread_pool(func, execution_hint):
            return await self._run_in_thread_pool(func, **kwargs)
        else:
            return await smart_call_async(func, **kwargs)

    async def _run_in_thread_pool(self, func: callable, **kwargs) -> Result[Any]:
        """Execute function in thread pool."""
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(self._thread_pool, lambda: func(**kwargs))
            return Ok(result)
        except (TypeError, ValueError) as e:
            return Result.error(f"Function execution in thread pool failed: {e}")

    async def _run_in_process_pool(self, func: callable, **kwargs) -> Result[Any]:
        """Execute function in process pool."""
        if self._process_pool is None:
            self._process_pool = ProcessPoolExecutor(max_workers=2)

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(self._process_pool, lambda: func(**kwargs))
            return Ok(result)
        except (TypeError, ValueError) as e:
            return Result.error(f"Function execution in process pool failed: {e}")