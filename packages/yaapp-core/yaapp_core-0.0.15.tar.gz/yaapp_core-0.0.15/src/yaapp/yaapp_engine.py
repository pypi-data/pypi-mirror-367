"""
YaappEngine - Core service provider for external objects.

This is the main interface that runners and plugins interact with.
Provides all services needed by external objects.
"""

import inspect
from typing import Any, Dict, List, Optional, Union

from .executor import Executor

# Import the new exposer classes
from .exposers.class_exposer import ClassExposer
from .exposers.custom import CustomExposer
from .exposers.function import FunctionExposer
from .exposers.object import ObjectExposer
from .registry import Registry
from .result import Ok, Result
from .config import Config


# TODO remove the command, is boilerplate. We introduced as the execute was having issues with kwargs containinng 'name' parameter.
class Command:
    """Defensive command wrapper that prevents parameter name conflicts."""

    def __init__(
        self, name: str, metadata: Dict[str, Any], exposer: Any, engine: "YaappEngine"
    ):
        self.name = name
        self.metadata = metadata
        self.exposer = exposer
        self.engine = engine

    async def execute(self, **kwargs) -> Result[Any]:
        """Execute the command with parameters.

        This method avoids parameter name conflicts by not using 'name' as a parameter.
        """
        # Extract subcommand name if provided
        subcommand_name = kwargs.pop('subcommand_name', None)
        
        # If it's a group (class or object instance), we need to execute its subcommands
        if self.metadata.get("type") == "group":
            # The 'run' method of ClassExposer/ObjectExposer returns an instance
            instance_result = self.exposer.run(self.metadata.get("obj"), yaapp_engine=self.engine, **kwargs)
            if not inspect.isawaitable(instance_result):
                if instance_result.is_err():
                    return instance_result
                instance = instance_result.unwrap()
            else:
                instance_result = await instance_result
                if instance_result.is_err():
                    return instance_result
                instance = instance_result.unwrap()

            # If a subcommand name is provided via dot notation, execute that subcommand on the instance
            if subcommand_name:
                return await self.engine.object_exposer.run(
                    instance, subcommand_name, **kwargs
                )
            else:
                # If no subcommand_name, and it's a group, return the instance itself
                return Ok(instance)
        else:  # It's a command (function or custom object)
            # The 'run' method of FunctionExposer/CustomExposer executes the command
            result = self.exposer.run(
                self.metadata.get("obj"), yaapp_engine=self.engine, **kwargs
            )
            if not inspect.isawaitable(result):
                return result
            else:
                return await result

    def subcommand(self, name: str) -> Result['Command']:
        pass

    def is_ok(self) -> bool:
        """Always returns True since Command objects are only created for valid commands."""
        return True

    def get_metadata(self) -> Dict[str, Any]:
        """Get command metadata."""
        return self.metadata.copy()


class YaappEngine:
    """Core service provider for runners and plugins.

    This is what external objects (runners/plugins) receive and interact with.
    Provides all services they need without exposing internal complexity.
    """

    def __init__(self):
        """Initialize the engine with core components.

        NOTE: Constructor is lightweight - no I/O operations!
        Call activate() for full initialization with config loading.
        """
        self.registry = Registry()  # Create own registry instance
        self.executor = Executor(self.registry)  # Create executor with registry
        self._plugins_discovered = False
        self._runners_discovered = False
        self._activated = False  # Track activation state
        self._runner_manager = None  # Lazy-loaded runner manager
        self._plugin_path = None  # Plugin search paths
        self._config = Config()  # Config instance

        # Simple cache for runners (NOT in registry - runners are infrastructure)
        self._runners_cache: Dict[str, Any] = {}

        # Instantiate the new exposer classes
        self.class_exposer = ClassExposer()
        self.function_exposer = FunctionExposer()
        self.object_exposer = ObjectExposer()
        self.custom_exposer = CustomExposer()

        # Apply any pending @expose registrations immediately (sync operation)
        self._apply_pending_registrations()

        # Register core service
        self._register_core_service()

    def _apply_pending_registrations(self):
        """Apply pending @expose registrations."""
        from .expose import apply_pending_registrations

        apply_pending_registrations(self)

    def _register_core_service(self):
        """Register the core service."""
        from .core_service import register_core_service

        register_core_service(self)

    async def activate(self) -> Result[bool]:
        """Activate the engine - load config and plugins asynchronously.

        This method handles:
        - Loading configuration (local files, network, etc.)
        - Discovering and activating plugins
        - Setting up runners

        Returns:
            Result[bool]: Success/failure of activation
        """
        if self._activated:
            return Ok(True)

        try:
            # Load configuration asynchronously
            config_result = await self._load_config_async()
            if config_result.is_err():
                return config_result

            # Activate plugins based on config
            plugins_result = await self._activate_plugins_async()
            if plugins_result.is_err():
                return plugins_result

            self._activated = True
            return Ok(True)

        except (AttributeError, TypeError) as e:
            return Result.error(f"Engine activation failed: {str(e)}")

    async def _load_config_async(self) -> Result[bool]:
        """Load configuration asynchronously using the new Config system."""
        try:
            # Load configuration using the new Config class
            config_result = await self._config.load_config()
            if config_result.is_err():
                return config_result
            
            return Ok(True)

        except (ImportError, AttributeError, TypeError, ValueError) as e:
            # Protect against foreign library issues (yaml, json, file I/O)
            return Result.error(f"Config loading failed: {str(e)}")

    async def _activate_plugins_async(self) -> Result[bool]:
        """Activate plugins asynchronously.

        Future: This will support async plugin initialization.
        """
        try:
            # Discover plugins if not already done
            if not self._plugins_discovered:
                self._discover_and_register_plugins()

            # Activate plugins from config if specified
            self.activate_plugins_from_config()

            return Ok(True)

        except (ImportError, AttributeError, TypeError, ValueError) as e:
            return Result.error(f"Plugin activation failed: {str(e)}")

    def is_activated(self) -> bool:
        """Check if engine is fully activated."""
        return self._activated

    # TODO remove the command, is boilerplate. We introduced as the execute was having issues with kwargs containinng 'name' parameter.
    def command(self, name: str) -> Result["Command"]:
        """Get a command object for defensive execution.

        Returns:
            Result[Command]: Command object if found, error if not found
        """
        # Check if command exists
        registry_item_result = self.registry.get_both(name)
        if registry_item_result.is_err():
            return Result.error(
                f"Command '{name}' not found: {registry_item_result.as_error}"
            )

        metadata, exposer = registry_item_result.unwrap()

        # Return a Command wrapper
        return Ok(Command(name, metadata, exposer, self))

    async def execute(self, ____name: str, **kwargs) -> Result[Any]:
        """Execute a command - main service for external objects.
        
        Args:
            ____name: Command name to execute. Supports dot notation for subcommands (e.g., "class.subcommand")
                     Uses ugly ____name to avoid conflicts with user kwargs.
            **kwargs: Arguments to pass to the command
        """
        # Handle dot notation for subcommand calls (class.subcommand)
        subcommand_name = None
        if "." in ____name:
            class_name, subcommand_name = ____name.split(".", 1)
            ____name = class_name
        
        # Retrieve the metadata and exposer from the registry
        registry_item_result = self.registry.get_both(____name)
        if registry_item_result.is_err():
            return Result.error(
                f"Command '{____name}' not found: {registry_item_result.as_error}"
            )

        metadata, exposer = registry_item_result.unwrap()

        # If it's a group (class or object instance), we need to execute its subcommands
        if metadata.get("type") == "group":
            # For ObjectExposer, we need a subcommand name - can't instantiate objects
            if (hasattr(exposer, "__class__") and exposer.__class__.__name__ == "ObjectExposer"):
                if not subcommand_name:
                    return Result.error(f"Object '{____name}' requires a subcommand (e.g., '{____name}.method_name')")
                # For ObjectExposer, we already have the instance, so call the subcommand directly
                return await exposer.run(
                    metadata.get("obj"), subcommand_name, **kwargs
                )
            
            # For ClassExposer, the 'run' method returns an instance
            # It might return an Err directly if instantiation fails
            instance_result = exposer.run(metadata.get("obj"), yaapp_engine=self, **kwargs)
            if not inspect.isawaitable(instance_result):
                if instance_result.is_err():
                    return instance_result
                instance = instance_result.unwrap()
            else:
                instance_result = await instance_result
                if instance_result.is_err():
                    return instance_result
                instance = instance_result.unwrap()

            # If a subcommand name is provided via dot notation, execute that subcommand on the instance
            if subcommand_name:
                # This is for ClassExposer case - we have an instance and need to call a method on it
                return await self.object_exposer.run(
                    instance, subcommand_name, **kwargs
                )
            else:
                # If no subcommand_name, and it's a group, return the instance itself
                return Ok(instance)
        else:  # It's a command (function or custom object)
            # The 'run' method of FunctionExposer/CustomExposer executes the command
            result = exposer.run(metadata.get("obj"), yaapp_engine=self, **kwargs)
            if not inspect.isawaitable(result):
                return result
            else:
                return await result

    def expose(self, obj: Any, name: Optional[str] = None, **kwargs) -> None:
        """Expose an object - main service for plugins."""
        # Determine name
        actual_name = name or getattr(obj, "__name__", str(obj))

        # Determine exposer type and get metadata
        custom = kwargs.get("custom", False)

        exposer_instance: Any  # Will hold the specific exposer instance
        metadata_result: Result[Dict[str, Any]]

        if custom:
            exposer_instance = self.custom_exposer
            metadata_result = exposer_instance.get_metadata(obj)
        elif inspect.isclass(obj):
            exposer_instance = self.class_exposer
            metadata_result = exposer_instance.get_metadata(obj)
        elif callable(obj):
            exposer_instance = self.function_exposer
            metadata_result = exposer_instance.get_metadata(obj)

        else:
            exposer_instance = self.object_exposer
            metadata_result = exposer_instance.get_metadata(obj)

        if metadata_result.is_ok():
            metadata = metadata_result.unwrap()
            metadata["obj"] = obj  # Store the original object
            # Store the metadata and the exposer instance in the registry
            self.registry.add(actual_name, metadata, exposer_instance)
        else:
            print(
                f"Warning: Failed to expose {actual_name}: {metadata_result.as_error}"
            )

    def activate_plugin(self, plugin_name: str, plugin_config: Dict[str, Any]) -> None:
        """Activate a plugin with config - loads plugin only when needed."""
        try:
            from .plugin_discovery import discover_plugins_metadata, load_plugin_class

            # Get plugin metadata (no imports)
            plugin_path = self.get_plugin_path()
            plugins_metadata = discover_plugins_metadata(plugin_path)

            if plugin_name not in plugins_metadata:
                print(f"Warning: Plugin '{plugin_name}' not found in plugin paths")
                return

            # NOW load the plugin class (import happens here)
            plugin_metadata = plugins_metadata[plugin_name]
            plugin_class = load_plugin_class(plugin_metadata)

            if not plugin_class:
                print(f"Warning: Failed to load plugin class for '{plugin_name}'")
                return

            if not inspect.isclass(plugin_class):
                print(f"Warning: Plugin '{plugin_name}' object is not a class.")
                return

            # Instantiate with config
            plugin_instance = plugin_class(plugin_config)

            # Run plugin to register its functionality
            self.run_plugin(plugin_instance)

            # Apply any new pending registrations from the plugin
            self._apply_pending_registrations()

        except (ImportError, AttributeError, TypeError, ValueError) as e:
            # Protect against plugin instantiation issues (foreign code)
            print(f"Warning: Failed to activate plugin '{plugin_name}': {e}")

    # ===== QUERY SERVICES (LAZY DISCOVERY) =====
    def get_commands(self) -> Dict[str, Any]:
        """Get available commands - service for runners."""
        # Filter out internal objects (plugins/runners) and return their metadata
        commands = {}
        for name, item_tuple in self.registry.list_items().items():
            # item_tuple is (metadata, exposer_instance)
            metadata = item_tuple[0]
            if not name.startswith("_") and metadata.get("type") in [
                "command",
                "group",
            ]:
                commands[name] = metadata  # Return the metadata directly
        return commands

    def get_plugins(self) -> Dict[str, Any]:
        """Get available plugins - filesystem discovery, NO imports."""
        from .plugin_discovery import discover_plugins_metadata

        # Use configured plugin path
        plugin_path = self.get_plugin_path()
        plugins_metadata = discover_plugins_metadata(plugin_path)

        # Convert to expected format
        plugins = {}
        for plugin_name, metadata in plugins_metadata.items():
            plugins[plugin_name] = {
                "name": plugin_name,
                "type": "plugin",
                "help": "Plugin functionality",
                "path": metadata["path"],
                "discovered": metadata["discovered"],
                "loaded": metadata["loaded"],
            }

        return plugins

    def get_runners(self) -> Dict[str, Any]:
        """Get available runners from cache - lazy discovery."""
        if not self._runners_discovered:
            self._discover_and_register_runners()

        # Return runners from cache with metadata
        runners = {}
        for name, runner_module in self._runners_cache.items():
            runners[name] = {
                "name": name,
                "type": "runner",
                "help": self._get_runner_help(runner_module),
                "module": runner_module,
            }
        return runners

    def get_command_tree(self) -> Dict[str, Any]:
        """Get hierarchical command structure - service for runners."""
        # Now directly return the metadata from the registry
        commands = self.get_commands()
        command_tree = {}
        for name, metadata in commands.items():
            command_tree[name] = metadata
        return command_tree

    def get_command_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata about a command - service for runners."""
        result = self.registry.get_both(name)
        if not result.is_ok():
            return {}

        metadata, exposer = result.unwrap()
        return metadata  # Return the stored metadata directly

    def get_command_help(self, command_name: str) -> str:
        """Get help text for a command - service for runners."""
        commands = self.get_commands()
        if command_name not in commands:
            return "Command not found"
        
        metadata = commands[command_name]
        obj = metadata.get('obj')
        if obj and hasattr(obj, '__doc__') and obj.__doc__:
            return obj.__doc__.strip().split('\n')[0]
        return "Command available"
    
    def get_subcommand_help(self, command_name: str, subcommand_name: str) -> str:
        """Get help text for a subcommand - service for runners."""
        commands = self.get_commands()
        if command_name not in commands:
            return "Command not found"
        
        metadata = commands[command_name]
        if metadata.get('type') != 'group':
            return "Not a command group"
            
        subcommands = metadata.get('commands', {})
        if subcommand_name not in subcommands:
            return "Subcommand not found"
            
        subcommand_info = subcommands[subcommand_name]
        if isinstance(subcommand_info, dict) and 'help' in subcommand_info:
            help_text = subcommand_info['help']
            if help_text and help_text.strip() and help_text.strip() != "No description.":
                return help_text.strip()
        return "Subcommand available"
    
    def get_method_help(self, command_name: str, method_name: str) -> str:
        """Get help text for a class method - service for runners.
        
        DEPRECATED: Use get_subcommand_help() instead.
        """
        return self.get_subcommand_help(command_name, method_name)

    # ===== PLUGIN SERVICES =====
    def register_plugin(self, name: str, plugin: Any) -> None:
        """Register a plugin instance in the registry."""
        # Store in registry with _plugin_ prefix
        # Plugins are now exposed via expose() so they get metadata
        self.expose(plugin, f"_plugin_{name}")

    def run_plugin(self, plugin: Any) -> None:
        """Run a plugin - calls plugin.run(yaapp_engine=self)."""
        if hasattr(plugin, "run"):
            plugin.run(yaapp_engine=self)

    # ===== RUNNER SERVICES =====
    def register_runner(self, name: str, runner_module: Any) -> None:
        """Register a runner module in simple cache (NOT registry)."""
        # Store runner module in cache - runners are infrastructure, not commands
        self._runners_cache[name] = runner_module

    def get_runner_module(self, name: str) -> Optional[Any]:
        """Get runner module by name from cache."""
        if not self._runners_discovered:
            self._discover_and_register_runners()

        return self._runners_cache.get(name)

    def _get_runner_help(self, runner_module: Any) -> str:
        """Get help text from runner module."""
        if hasattr(runner_module, "help") and callable(runner_module.help):
            try:
                help_text = runner_module.help()
                # Clean up help text - take first line
                if isinstance(help_text, str):
                    return help_text.strip().split("\n")[0]
            except (AttributeError, TypeError):
                pass
        return f"Runner: {getattr(runner_module, '__name__', 'Unknown')}"

    # ===== PRIVATE DISCOVERY METHODS =====
    def _discover_and_register_plugins(self) -> None:
        """Discover and register available plugins."""
        if self._plugins_discovered:
            return

        from .plugin_discovery import discover_plugins

        # Use configured plugin path
        plugin_path = self.get_plugin_path()
        discovered = discover_plugins(plugin_path)
        for name, plugin_class in discovered.items():
            self.register_plugin(name, plugin_class)

        self._plugins_discovered = True

    def _discover_and_register_runners(self) -> None:
        """Discover and register available runners."""
        if self._runners_discovered:
            return

        from .plugin_discovery import discover_runners

        discovered = discover_runners()
        for name, runner_class in discovered.items():
            self.register_runner(name, runner_class)

        self._runners_discovered = True

    # ===== RUNNER MANAGEMENT =====
    def get_runner_manager(self):
        """Get runner manager - lazy loaded."""
        if self._runner_manager is None:
            from .runner_manager import RunnerManager

            self._runner_manager = RunnerManager(self)
        return self._runner_manager

    def run(self, runner=None, **kwargs):
        """Run with specified runner.

        Args:
            runner: Runner name, instance, or None for default
            **kwargs: Arguments to pass to runner
        """
        # Ensure engine is activated before running
        if not self.is_activated():
            import asyncio

            result = asyncio.run(self.activate())
            if result.is_err():
                print(f"Warning: Engine activation failed: {result.as_error}")

        runner_manager = self.get_runner_manager()
        result = runner_manager.run(runner, **kwargs)
        if result.is_err():
            print(f"Error: Runner execution failed: {result.as_error}")

    def get_available_runners(self) -> list:
        """Get available runner names."""
        runner_manager = self.get_runner_manager()
        return runner_manager.get_available_runners()

    def get_core_services(self) -> Dict[str, Any]:
        """Get core services from registry."""
        core_services = {}
        for name, item_tuple in self.registry.list_items().items():
            # item_tuple is (metadata, exposer_instance)
            metadata = item_tuple[0]
            if name == "core":  # Core service
                core_services[name] = metadata  # Return the metadata
        return core_services

    # ===== PLUGIN PATH SERVICES =====
    def set_plugin_path(self, plugin_path: str) -> None:
        """Set plugin search paths.

        Args:
            plugin_path: Colon-separated paths to search for plugins
        """
        self._plugin_path = plugin_path
        # Reset discovery to force re-discovery with new paths
        self._plugins_discovered = False

    def get_plugin_path(self) -> str:
        """Get plugin search paths.

        Returns:
            Colon-separated plugin search paths
        """
        if self._plugin_path:
            return self._plugin_path

        # Default plugin paths
        import os

        default_paths = [
            "src/yaapp/plugins",
            "third_party/yaapp-plugins/src/yaapp/plugins",
        ]
        return ":".join(default_paths)

    # ===== CONFIGURATION SERVICES =====
    async def get_config(self, path: str) -> Result[Any]:
        """Get configuration value by dot notation path.
        
        This method provides developers access to configuration values using
        dot notation paths like 'server.host', 'database.url', 'logging.level'.
        
        Args:
            path: Configuration path in dot notation (e.g., 'server.host', 'database.port')
        
        Returns:
            Result[Any]: Ok with the configuration value if found, 
                        Err with "path not found" message if the path doesn't exist
        
        Examples:
            # Get server host configuration
            result = await engine.get_config('server.host')
            if result.is_ok():
                host = result.unwrap()  # e.g., 'localhost'
            
            # Get nested configuration
            result = await engine.get_config('database.connection.timeout')
            if result.is_ok():
                timeout = result.unwrap()  # e.g., 30
            
            # Handle missing configuration
            result = await engine.get_config('nonexistent.path')
            if result.is_err():
                error_msg = result.as_error  # "path not found"
        """
        # Ensure config is loaded
        if not self._activated:
            activate_result = await self.activate()
            if activate_result.is_err():
                return Result.error(f"Failed to activate engine for config access: {activate_result.as_error}")
        
        # Get value from config using dot notation  
        return await self._config.get(path)

    async def set_config(self, path: str, value: Any) -> Result[bool]:
        """Set configuration value by dot notation path for runtime injection.
        
        This method allows developers to inject configuration values at runtime,
        supporting dynamic reconfiguration of the system.
        
        Args:
            path: Configuration path in dot notation (e.g., 'database.host', 'server.port')
            value: Value to set (can be string, int, dict, list, etc.)
        
        Returns:
            Result[bool]: Ok(True) if successful, Err with error message if failed
        
        Examples:
            # Set simple values
            result = await engine.set_config('database.host', 'prod.db.com')
            
            # Set nested configuration
            result = await engine.set_config('server.ssl.enabled', True)
            
            # Set complex configuration
            result = await engine.set_config('database.pool', {
                'min_connections': 5,
                'max_connections': 20
            })
        """
        # Ensure config is loaded
        if not self._activated:
            activate_result = await self.activate()
            if activate_result.is_err():
                return Result.error(f"Failed to activate engine for config access: {activate_result.as_error}")
        
        # Set value in config
        return await self._config.set(path, value)

    def activate_plugins_from_config(self) -> None:
        """Activate plugins listed in config.plugins section.
        
        Simple and clean mechanism consistent with CLI --plugin processing:
        1. Get plugins section from config
        2. Discover available plugins  
        3. Activate each plugin with its config
        
        Expected config format:
            plugins:
              storage:
                type: redis
                host: localhost
              auth:  
                provider: oauth
                enabled: true
        """
        try:
            # Get config data
            config_data = self._config.to_dict()
            if 'plugins' not in config_data:
                return  # No plugins section - nothing to activate
                
            plugins_section = config_data['plugins']
            if not isinstance(plugins_section, dict):
                print("Warning: config.plugins should be a dictionary")
                return
                
            # Get available plugins (same as CLI --plugin mechanism)
            available_plugins = self.get_plugins()
            
            # Activate each plugin listed in config
            for plugin_name, plugin_config in plugins_section.items():
                if plugin_name in available_plugins:
                    # Use same activation method as CLI runners
                    plugin_config_dict = plugin_config if isinstance(plugin_config, dict) else {}
                    self.activate_plugin(plugin_name, plugin_config_dict)
                    print(f"✅ Activated plugin from config: {plugin_name}")
                else:
                    print(f"Warning: Plugin '{plugin_name}' not found in plugin paths")
                    print(f"  Available plugins: {list(available_plugins.keys())}")
                    
        except Exception as e:
            print(f"Warning: Failed to activate plugins from config: {e}")


# No singleton - each Yaapp instance creates its own YaappEngine
