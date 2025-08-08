"""
Core service for yaapp - provides core commands that don't depend on plugins.
This service gets registered to the registry and can be queried by any runner.
"""

from .result import Result, Ok
from . import __version__


class CoreService:
    """Core yaapp service providing essential commands."""
    
    def __init__(self):
        """Initialize core service."""
        self.name = "core"
    
    def init(self):
        """Initialize a new yaapp project."""
        print("yaapp core init - Initialize a new yaapp project")
        # TODO: Create yaapp.yaml template
        return "Project initialized"
    
    def status(self):
        """Show yaapp project status."""
        print("yaapp core status - Show project status")
        # TODO: Show config, plugins, etc.
        return "Status: OK"
    
    def config(self):
        """Show configuration."""
        print("yaapp core config - Show current configuration")
        # TODO: Show current config
        return "Configuration displayed"
    
    def version(self):
        """Show yaapp version."""
        return f"yaapp {__version__}"


def register_core_service(yaapp_engine):
    """Register the core service to the yaapp engine registry."""
    core_service = CoreService()
    yaapp_engine.expose(core_service, "core")
    return core_service