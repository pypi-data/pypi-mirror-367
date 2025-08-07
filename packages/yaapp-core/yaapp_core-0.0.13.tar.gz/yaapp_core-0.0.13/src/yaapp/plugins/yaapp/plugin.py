"""
Yaapp Plugin - Default plugin that exposes yaapp_engine functionality.

This plugin provides access to yaapp_engine methods through the command interface.
By exposing the class, methods become subcommands: yaapp.get_commands, yaapp.info, etc.
"""

from yaapp import expose


@expose(name="yaapp")
class Yaapp:
    """Yaapp plugin - exposes yaapp_engine functionality.

    When this class is exposed, each public method becomes a subcommand:
    - yaapp.get_commands
    - yaapp.get_plugins
    - yaapp.get_runners
    - yaapp.info
    - yaapp.status
    """

    def __init__(self, yaapp_engine, config=None):
        """Initialize with yaapp_engine and config."""
        self.yaapp_engine = yaapp_engine
        self.config = config or {}

    def run(self, yaapp_engine):
        """Plugin initialization - receives yaapp_engine."""
        self.yaapp_engine = yaapp_engine
        # No manual exposure needed - class exposure handles method exposure automatically

    def get_commands(self):
        """Get available commands from yaapp_engine."""
        return list(self.yaapp_engine.get_commands().keys())

    def get_plugins(self):
        """Get registered plugins from yaapp_engine."""
        return list(self.yaapp_engine.get_plugins().keys())

    def get_runners(self):
        """Get available runners from yaapp_engine."""
        return list(self.yaapp_engine.get_runners().keys())

    def info(self):
        """Get yaapp system information."""
        return {
            "commands": len(self.yaapp_engine.get_commands()),
            "plugins": len(self.yaapp_engine.get_plugins()),
            "runners": len(self.yaapp_engine.get_runners()),
            "config": self.config,
        }

    def status(self):
        """Get yaapp system status."""
        return {
            "status": "running",
            "plugins_discovered": self.yaapp_engine._plugins_discovered,
            "runners_discovered": self.yaapp_engine._runners_discovered,
            "config_loaded": self.yaapp_engine._config_loaded,
        }


# Also demonstrate standalone functions with @expose
@expose(name="hello")
def hello_function(name):
    """Say hello to someone (standalone function)."""
    return f"Hello, {name}!"


@expose(name="add")
def add_function(x, y):
    """Add two numbers (standalone function)."""
    try:
        return int(x) + int(y)
    except ValueError:
        return "Error: Please provide valid numbers"


def non_exposed_function(name):
    """This function is not exposed and won't be available as a command."""
    return "This function is not exposed to the command interface."
