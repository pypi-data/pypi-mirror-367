"""
Standalone expose functionality to avoid circular imports.

This module provides the expose decorator without importing any yaapp internals.
Plugin writers should use: from yaapp import expose
"""

# Global registry for lazy plugin registration
_pending_registrations = []

def expose(obj=None, name=None, custom=False, execution=None):
    """Expose a function, class, or object to yaapp without importing the singleton.
    
    This is the preferred way to expose plugins to avoid circular imports.
    Registrations are queued and applied when yaapp.run() is called.
    
    Args:
        obj: Function, class, or object to expose
        name: Optional name (defaults to function/class name)
        custom: Whether to use custom exposure workflow
        execution: Execution strategy hint
    
    Returns:
        Decorator function or result
    
    Usage:
        @expose(name="my_plugin")
        class MyPlugin:
            pass
            
        # Or
        @expose
        def my_function():
            pass
    """
    def decorator(target_obj):
        # Queue the registration for later
        _pending_registrations.append({
            'obj': target_obj,
            'name': name,
            'custom': custom,
            'execution': execution
        })
        return target_obj
    
    if obj is None:
        # Used as decorator: @expose or @expose(name="foo")
        return decorator
    else:
        # Used directly: expose(func, "name")
        return decorator(obj)

def get_pending_registrations():
    """Get all pending registrations."""
    return _pending_registrations.copy()

def clear_pending_registrations():
    """Clear all pending registrations."""
    global _pending_registrations
    _pending_registrations.clear()

def apply_pending_registrations(yaapp_engine):
    """Apply all pending registrations to the yaapp engine."""
    global _pending_registrations
    applied_count = 0
    for reg in _pending_registrations:
        # yaapp_engine.expose() should handle errors internally and not raise exceptions
        # If it does raise, that's a bug in the engine that should be fixed
        yaapp_engine.expose(
            reg['obj'], 
            reg['name'], 
            custom=reg['custom']
        )
        applied_count += 1
    
    # DON'T clear registrations - keep them for future engine instances
    # This allows multiple engines to be created with the same exposed functions
    # _pending_registrations.clear()  # REMOVED
    return applied_count