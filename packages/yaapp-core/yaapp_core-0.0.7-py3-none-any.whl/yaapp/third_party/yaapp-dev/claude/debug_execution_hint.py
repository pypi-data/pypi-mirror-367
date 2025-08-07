#!/usr/bin/env python3
"""
Debug the execution hint issue.
"""

import sys
sys.path.insert(0, 'src')

from yaapp import Yaapp
from yaapp.execution_strategy import get_execution_hint, ExecutionStrategy


def test_func(x: int) -> int:
    return x * 2


def main():
    app = Yaapp()
    
    # Test different execution strategies
    app.expose(test_func, name="direct_func", execution="direct")
    app.expose(test_func, name="thread_func", execution="thread")
    
    # Debug the functions
    direct_func, _ = app._registry["direct_func"]
    thread_func, _ = app._registry["thread_func"]
    
    print(f"Direct func: {direct_func}")
    print(f"Has hint: {hasattr(direct_func, '__execution_hint__')}")
    if hasattr(direct_func, '__execution_hint__'):
        hint = direct_func.__execution_hint__
        print(f"Direct hint: {hint}")
        print(f"Direct strategy: {hint.strategy}")
    
    print()
    print(f"Thread func: {thread_func}")
    print(f"Has hint: {hasattr(thread_func, '__execution_hint__')}")
    if hasattr(thread_func, '__execution_hint__'):
        hint = thread_func.__execution_hint__
        print(f"Thread hint: {hint}")
        print(f"Thread strategy: {hint.strategy}")
    
    # Test get_execution_hint
    direct_hint = get_execution_hint(direct_func)
    thread_hint = get_execution_hint(thread_func)
    
    print(f"\nget_execution_hint results:")
    print(f"Direct: {direct_hint.strategy}")
    print(f"Thread: {thread_hint.strategy}")


if __name__ == "__main__":
    main()