"""
Utilities for the exposer system.
"""
import inspect
from typing import Any, Dict, List

def _reflect_class_commands(cls: type) -> Dict[str, Dict[str, Any]]:
    """
    Reflects on a class and returns metadata for all its public methods as commands.
    This is the single source of truth for class reflection.
    """
    commands = {}
    for name in dir(cls):
        if name.startswith('_'):
            continue

        try:
            value = getattr(cls, name)
            if callable(value) and not inspect.isclass(value):
                commands[name] = _reflect_function(value)
        except (AttributeError, TypeError):
            # Skip attributes that cause errors during inspection
            continue
    return commands

def _reflect_function(func: callable) -> Dict[str, Any]:
    """
    Reflects on a single function/method and returns its metadata.
    """
    docstring = inspect.getdoc(func) or "No description."
    short_doc = docstring.split('\n')[0]

    metadata: Dict[str, Any] = {
        "type": "command",
        "help": short_doc,
        "params": {}
    }

    try:
        sig = inspect.signature(func)
        for param in sig.parameters.values():
            if param.name == 'self':
                continue
            
            param_type = str if param.annotation == inspect.Parameter.empty else param.annotation
            
            metadata["params"][param.name] = {
                "type": param_type,
                "default": param.default if param.default != inspect.Parameter.empty else None,
                "required": param.default == inspect.Parameter.empty
            }
    except (ValueError, TypeError):
        # Cannot inspect signature, treat as a command with no params
        pass

    return metadata
