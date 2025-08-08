"""
Click CLI runner for yaapp.
Provides the main CLI interface with runner and plugin selection.
This is the equivalent of the UnifiedCLIBuilder from the root implementation.
"""


def help():
    """Return click runner help text."""
    return """
🖱️ CLICK CLI RUNNER: Main CLI interface with runner and plugin selection
  --runner        Select runner (click, prompt, server, etc.)
  --plugin        Load specific plugin
  --list-runners  List all available runners
    """


def run(yaapp_engine, **kwargs):
    """Execute the Click runner - creates the main CLI with all options."""
    try:
        import sys

        import click
    except ImportError:
        print("click not available. Install with: pip install click")
        return

    # Pre-process plugin-path before building the CLI
    if "--plugin-path" in sys.argv:
        plugin_path = None
        args_to_remove = []
        for i, arg in enumerate(sys.argv):
            if arg == "--plugin-path" and i + 1 < len(sys.argv):
                plugin_path = sys.argv[i + 1]
                args_to_remove.extend([i, i + 1])
                break

        if plugin_path:

            yaapp_engine.set_plugin_path(plugin_path)
            # Remove the plugin-path options from sys.argv so click doesn't see them again
            for i in sorted(args_to_remove, reverse=True):
                sys.argv.pop(i)

    # Pre-load plugins before building the CLI
    if "--plugin" in sys.argv or "-p" in sys.argv:
        plugin_name = None
        args_to_remove = []
        for i, arg in enumerate(sys.argv):
            if (arg == "--plugin" or arg == "-p") and i + 1 < len(sys.argv):
                plugin_name = sys.argv[i + 1]
                args_to_remove.extend([i, i + 1])
                break

        if plugin_name:
            _load_plugin_by_name(yaapp_engine, plugin_name)
            # Remove the plugin options from sys.argv so click doesn't see them again
            for i in sorted(args_to_remove, reverse=True):
                sys.argv.pop(i)

    # Build and run the main CLI
    cli = _build_main_cli(yaapp_engine)

    # Run the CLI
    cli()


def _build_main_cli(yaapp_engine):
    """Build the main CLI with all options (equivalent to UnifiedCLIBuilder)."""
    import click

    class CustomGroup(click.Group):
        """Custom Click group that separates core commands from plugin commands."""

        def format_commands(self, ctx, formatter):
            """Format commands with separate sections for core and plugin commands."""
            commands = []
            core_commands = []

            for subcommand in self.list_commands(ctx):
                cmd = self.get_command(ctx, subcommand)
                if cmd is None:
                    continue

                if subcommand == "core" and hasattr(cmd, "commands"):  # It's a group
                    core_commands.append((subcommand, cmd))
                elif (
                    subcommand == "core"
                ):  # It's a command, skip it from regular commands
                    continue
                else:
                    commands.append((subcommand, cmd))

            # Format core commands section
            if core_commands:
                with formatter.section("Core Commands"):
                    formatter.write_dl(
                        [
                            (cmd_name, cmd.get_short_help_str(limit=45))
                            for cmd_name, cmd in core_commands
                        ]
                    )

            # Format plugin commands section
            if commands:
                with formatter.section("Commands"):
                    formatter.write_dl(
                        [
                            (cmd_name, cmd.get_short_help_str(limit=45))
                            for cmd_name, cmd in commands
                        ]
                    )

    @click.group(cls=CustomGroup, invoke_without_command=True)
    @click.option("--verbose", "-v", is_flag=True, help="Verbose output")
    @click.option("--config", "-c", type=str, help="Configuration file path")
    @click.option("--plugin", "-p", type=str, help="Load specific plugin")
    @click.option("--plugin-path", type=str, help="Colon-separated plugin search paths")
    @click.option(
        "--suite",
        "-s",
        is_flag=True,
        help="Load complete plugin suite (all plugins as root commands)",
    )
    @click.option(
        "--list-plugins", "-l", is_flag=True, help="List all available plugins"
    )
    @click.option("--version", is_flag=True, help="Show version and exit")
    @click.option(
        "--runner",
        "-r",
        type=str,
        help="Run with specific runner (server, prompt, rich, typer, etc.)",
    )
    @click.option("--list-runners", is_flag=True, help="List all available runners")
    @click.pass_context
    def cli(
        ctx,
        verbose,
        config,
        plugin,
        plugin_path,
        suite,
        list_plugins,
        version,
        runner,
        list_runners,
    ):
        """Yaapp CLI with dynamically discovered runner options."""

        # Handle core yaapp options first
        if version:
            import asyncio
            result = asyncio.run(yaapp_engine.execute("core.version"))
            if result.is_ok():
                print(result.unwrap())
            else:
                print("yaapp (version unavailable)")
            ctx.exit()

        if list_plugins:
            _list_available_plugins(yaapp_engine)
            ctx.exit()

        if list_runners:
            _list_available_runners(yaapp_engine)
            ctx.exit()

        if config:
            print(f"Loading config from: {config}")
            # TODO: Handle config file loading

        if plugin_path:

            # Store plugin path in yaapp_engine for discovery
            yaapp_engine.set_plugin_path(plugin_path)

        if plugin:
            _load_plugin_by_name(yaapp_engine, plugin)
            # After loading the plugin, re-build the CLI and dispatch
            new_cli = _build_main_cli(yaapp_engine)
            # Find the original command arguments
            original_args = ctx.args
            # If the plugin option is still in the args, remove it
            if "-p" in original_args:
                p_index = original_args.index("-p")
                original_args.pop(p_index)
                if p_index < len(original_args) and original_args[p_index] == plugin:
                    original_args.pop(p_index)
            if "--plugin" in original_args:
                p_index = original_args.index("--plugin")
                original_args.pop(p_index)
                if p_index < len(original_args) and original_args[p_index] == plugin:
                    original_args.pop(p_index)

            with new_cli.make_context(cli.name, original_args) as new_ctx:
                new_cli.invoke(new_ctx)
                ctx.exit()

        if suite:
            print("🚀 Loading complete plugin suite...")
            # TODO: Load all plugins

        if runner:
            _run_specific_runner(yaapp_engine, runner, ctx, verbose)
            return

        if ctx.invoked_subcommand is None:
            # No runner and no command - show help
            print(ctx.get_help())
            ctx.exit()

    # Add core commands first
    _add_core_commands(cli, yaapp_engine)

    # Add dynamic commands from yaapp_engine
    _add_dynamic_commands(cli, yaapp_engine)

    return cli


def _add_core_commands(cli, yaapp_engine):
    """Add core commands by querying core services from registry."""
    import click

    # Get core services from registry
    core_services = yaapp_engine.get_core_services()

    if "core" not in core_services:
        return  # No core service registered

    core_service = core_services["core"]

    @cli.group()
    def core():
        """Core yaapp commands that don't depend on plugins."""
        pass

    @core.command()
    def init():
        """Initialize a new yaapp project."""
        import asyncio

        # TODO the execute should use "dot notation", like 'core.init'
        # there may be nested commonds in the future like 'core.plugin.init'
        result = asyncio.run(yaapp_engine.execute("core", method_name="init"))
        if result.is_ok():
            value = result.unwrap()
            if value is not None:
                print(f"Result: {value}")
        else:
            print(f"Error: {result.as_error}")

    @core.command()
    def status():
        """Show yaapp project status."""
        import asyncio

        # TODO the execute should use "dot netation"
        # TODO the execute should use "dot notation", like 'core.init'
        # there may be nested commonds in the future like 'core.plugin.init'
        result = asyncio.run(yaapp_engine.execute("core", method_name="status"))
        if result.is_ok():
            value = result.unwrap()
            if value is not None:
                print(f"Result: {value}")
        else:
            print(f"Error: {result.as_error}")

    @core.command()
    def config():
        """Show configuration."""
        import asyncio

        result = asyncio.run(yaapp_engine.execute("core", method_name="config"))
        if result.is_ok():
            value = result.unwrap()
            if value is not None:
                print(f"Result: {value}")
        else:
            print(f"Error: {result.as_error}")

    @core.command()
    def version():
        """Show yaapp version."""
        import asyncio

        result = asyncio.run(yaapp_engine.execute("core", method_name="version"))
        if result.is_ok():
            value = result.unwrap()
            if value is not None:
                print(f"Result: {value}")
        else:
            print(f"Error: {result.as_error}")


def _add_dynamic_commands(cli, yaapp_engine):
    """Add dynamic commands from exposed functions/classes."""
    import inspect

    import click

    command_tree = yaapp_engine.get_command_tree()

    for name, info in command_tree.items():
        if name == "core":
            continue

        if name in cli.commands:
            continue

        if info["type"] == "command":
            obj = info["obj"]

            @click.command(name=name)
            @click.pass_context
            def cmd(ctx, **kwargs):
                """Execute function command."""
                # Filter out None values for kwargs that were not provided
                filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
                _execute_function_command(
                    yaapp_engine, ctx.info_name, **filtered_kwargs
                )

            if hasattr(obj, "__doc__") and obj.__doc__:
                cmd.__doc__ = obj.__doc__.strip().split("\n")[0]

            # Reflect parameters
            sig = inspect.signature(obj)
            for param in reversed(list(sig.parameters.values())):
                if param.default == inspect.Parameter.empty:
                    # Required option
                    cmd = click.option(
                        f"--{param.name}",
                        required=True,
                        help=f"Required parameter {param.name}",
                    )(cmd)
                else:
                    # Optional parameter
                    cmd = click.option(
                        f"--{param.name}",
                        default=param.default,
                        help=f"Optional parameter {param.name}",
                    )(cmd)

            cli.add_command(cmd)

        elif info["type"] == "group":
            obj = info["obj"]
            commands = info["commands"]

            @click.group(name=name)
            @click.pass_context
            def group_cmd(ctx):
                """Class command group."""
                pass

            if hasattr(obj, "__doc__") and obj.__doc__:
                group_cmd.__doc__ = obj.__doc__.strip().split("\n")[0]

            for method_name, method_info in commands.items():
                # Correctly get the method object from the class
                method_obj = getattr(obj, method_name, None)
                if not method_obj or not callable(method_obj):
                    continue

                @click.command(name=method_name)
                @click.pass_context
                def method_cmd(ctx, **kwargs):
                    """Execute class method."""
                    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
                    _execute_class_method(
                        yaapp_engine,
                        ctx.parent.info_name,
                        ctx.info_name,
                        **filtered_kwargs,
                    )

                if hasattr(method_obj, "__doc__") and method_obj.__doc__:
                    method_cmd.__doc__ = method_obj.__doc__.strip().split("\n")[0]

                # Reflect parameters for methods
                method_sig = inspect.signature(method_obj)
                for param in reversed(list(method_sig.parameters.values())):
                    if param.name == "self":
                        continue
                    # FIXED: Skip yaapp_engine parameter (first parameter after self)
                    if param.name == "yaapp_engine":
                        continue

                    if param.default == inspect.Parameter.empty:
                        method_cmd = click.option(
                            f"--{param.name}",
                            required=True,
                            help=f"Required parameter {param.name}",
                        )(method_cmd)
                    else:
                        method_cmd = click.option(
                            f"--{param.name}",
                            default=param.default,
                            help=f"Optional parameter {param.name}",
                        )(method_cmd)

                group_cmd.add_command(method_cmd)

            cli.add_command(group_cmd)


def _list_available_plugins(yaapp_engine):
    """List available plugins."""
    print("\n🔌 Available Plugins:")
    print("=" * 50)

    plugins = yaapp_engine.get_plugins()
    if plugins:
        for plugin_name in sorted(plugins.keys()):
            print(f"  📦 {plugin_name:<15} - Plugin functionality")

        print("\n💡 Usage Examples:")
        print(
            "   yaapp --plugin storage --runner server     # Start storage API server"
        )
        print(
            "   yaapp --plugin launcher --runner server    # Start launcher API server"
        )
    else:
        print("  ❌ No plugins found")


def _list_available_runners(yaapp_engine):
    """List all available runners using the yaapp_engine discovery system."""
    print("\n🏃 Available Runners:")
    print("=" * 40)

    try:
        # Use yaapp_engine's runner discovery system
        runners = yaapp_engine.get_runners()

        if runners:
            for runner_name, runner_info in sorted(runners.items()):
                help_text = runner_info.get("help", "Runner available")
                # Clean up help text - take first line
                if isinstance(help_text, str):
                    help_text = help_text.strip().split("\n")[0]
                    # Clean up help text
                    if ":" in help_text:
                        help_text = help_text.split(":", 1)[1].strip()
                print(f"  🏃 {runner_name:<12} - {help_text}")
        else:
            print("  ❌ No runners found")

        print("\n💡 Usage Examples:")
        print("   yaapp --runner server                    # Start web server")
        print("   yaapp --plugin storage --runner server   # Storage API server")
        print("   yaapp --runner prompt                    # Interactive shell")
        print("   yaapp -r rich                           # Rich TUI (short form)")

    except Exception as e:
        print(f"  ❌ Error listing runners: {e}")


def _run_specific_runner(yaapp_engine, runner_name, ctx, verbose=False):
    """Run a specific runner using yaapp_engine's runner system."""
    if verbose:
        print(f"🏃 Starting {runner_name} runner...")

    try:
        # Use yaapp_engine's runner management system
        runner_module = yaapp_engine.get_runner_module(runner_name)

        if not runner_module:
            print(f"❌ Runner '{runner_name}' not found")
            print("💡 Use --list-runners to see available options")
            return

        # Check if module has the required run function
        if hasattr(runner_module, "run") and callable(runner_module.run):
            # Call the standard interface: run(yaapp_engine, **kwargs)
            runner_module.run(yaapp_engine)
        else:
            print(f"❌ Runner '{runner_name}' missing run() function")

    except Exception as e:
        print(f"❌ Error running '{runner_name}': {e}")


def _execute_function_command(yaapp_engine, command_name, **kwargs):
    """Execute a function command using defensive API."""
    import asyncio

    try:
        # FIXED: Use defensive command API to avoid parameter name conflicts
        command_result = yaapp_engine.command(command_name)
        if not command_result.is_ok():
            print(f"Error: {command_result.as_error}")
            return
        command = command_result.unwrap()
        try:
            result = asyncio.run(command.execute(**kwargs))
        except (RuntimeError, asyncio.InvalidStateError, OSError) as e:
            print(f"Error: Failed to run async command: {e}")
            return
        if result.is_ok():
            value = result.unwrap()
            if value is not None:
                print(f"Result: {value}")
        else:
            print(f"Error: {result.as_error}")
    except (
        asyncio.TimeoutError,
        asyncio.CancelledError,
        asyncio.InvalidStateError,
        asyncio.IncompleteReadError,
        OSError,
        RuntimeError,
    ) as e:
        print(f"Error: Async operation failed: {e}")
    except (TypeError, ValueError, AttributeError) as e:
        print(f"Error: {e}")


def _execute_class_method(yaapp_engine, class_name, method_name, **kwargs):
    """Execute a class method."""
    import asyncio

    try:
        # First get the class instance
        try:
            result = asyncio.run(yaapp_engine.execute(class_name))
        except (RuntimeError, asyncio.InvalidStateError, OSError) as e:
            print(f"Error: Failed to run async class execution: {e}")
            return
        if result.is_ok():
            instance = result.unwrap()
            if hasattr(instance, method_name):
                method = getattr(instance, method_name)
                # FIXED: Inject yaapp_engine as first parameter for plugin methods
                method_result = method(yaapp_engine, **kwargs)
                if method_result is not None:
                    print(f"Result: {method_result}")
            else:
                print(f"Error: Method '{method_name}' not found on {class_name}")
        else:
            print(f"Error: {result.as_error}")
    except (
        asyncio.TimeoutError,
        asyncio.CancelledError,
        asyncio.InvalidStateError,
        asyncio.IncompleteReadError,
        OSError,
        RuntimeError,
    ) as e:
        print(f"Error: Async operation failed: {e}")
    except (TypeError, ValueError, AttributeError) as e:
        print(f"Error: {e}")


def _load_plugin_by_name(yaapp_engine, plugin_name):
    """Load a specific plugin by name using discovery."""
    try:
        # Force plugin discovery to find the plugin
        yaapp_engine._plugins_discovered = False
        plugins = yaapp_engine.get_plugins()

        if plugin_name in plugins:
            # Plugin found in discovery, activate it
            yaapp_engine.activate_plugin(plugin_name, {})

        else:
            print(f"❌ Plugin '{plugin_name}' not found in plugin paths")
            print(f"Available plugins: {list(plugins.keys())}")

    except (ImportError, AttributeError, TypeError, ValueError) as e:
        print(f"❌ Failed to load plugin '{plugin_name}': {e}")
