#!/usr/bin/env python3
"""
Streaming Demo - yaapp with automatic SSE endpoints.

This example demonstrates yaapp's automatic streaming detection.
Generator functions automatically get /function/stream endpoints.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path for development  
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from yaapp import yaapp


@yaapp.expose
async def auto_counter(end: int = 5):
    """Count from 0 to end with 1 second delays."""
    for i in range(end + 1):
        yield {"count": i, "timestamp": time.time()}
        await asyncio.sleep(1.0)


@yaapp.expose  
async def simulate_progress(steps: int = 5):
    """Simulate progress from 0% to 100%."""
    for step in range(steps + 1):
        percentage = (step / steps) * 100 if steps > 0 else 100
        yield {
            "step": step, 
            "percentage": round(percentage, 1),
            "status": "completed" if step == steps else "processing"
        }
        await asyncio.sleep(0.8)


@yaapp.expose
def regular_function(message: str = "Hello"):
    """Regular function for comparison."""
    return {"message": message, "timestamp": time.time()}


if __name__ == "__main__":
    print("🚀 Streaming Demo")
    print("Streaming functions automatically get /function/stream endpoints")
    print("Available endpoints:")
    print("  GET /auto_counter/stream")
    print("  GET /simulate_progress/stream") 
    print("  POST /regular_function")
    yaapp.run()