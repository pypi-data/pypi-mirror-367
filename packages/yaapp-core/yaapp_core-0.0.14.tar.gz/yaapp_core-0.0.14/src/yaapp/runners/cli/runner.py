"""
Simple CLI runner for yaapp.
Provides clean argument parsing without heavy framework dependencies.

Structure: yaapp [ROOT_OPTIONS] [COMMAND_CHAIN] [COMMAND_ARGS]
- ROOT_OPTIONS: --help, --plugin X, --runner Y, --list-plugins, --version, etc.  
- COMMAND_CHAIN: command1 subcommand2 subcommand3...
- COMMAND_ARGS: --arg1 value1 --arg2 value2

Key rule: ROOT_OPTIONS must come before any commands.
"""

import sys
import inspect
from typing import Dict, List, Any, Optional, Tuple



def help():
    """Return CLI runner help text."""
    return "Simple CLI runner without framework dependencies"


def run(yaapp_engine, **kwargs):
    """Main entry point - parse args and dispatch."""
    args = sys.argv[1:]  # Skip script name
    
    if not args:
        show_main_help(yaapp_engine)
        return
    
    # Parse root options and find command boundary
    parsed = parse_arguments(args)
    
    if parsed['action'] == 'help':
        show_contextual_help(yaapp_engine, parsed)
    elif parsed['action'] == 'version':
        import asyncio
        result = asyncio.run(yaapp_engine.execute("core.version"))
        if result.is_ok():
            print(result.unwrap())
        else:
            print("yaapp (version unavailable)")
    elif parsed['action'] == 'list_plugins':
        list_plugins(yaapp_engine)
    elif parsed['action'] == 'list_runners':
        list_runners(yaapp_engine)
    elif parsed['action'] == 'switch_runner':
        switch_runner(yaapp_engine, parsed['runner'])
    elif parsed['action'] == 'execute':
        execute_command(yaapp_engine, parsed)
    else:
        show_main_help(yaapp_engine)


def parse_arguments(args: List[str]) -> Dict[str, Any]:
    """
    Parse arguments into root options and command execution.
    
    Returns dict with:
    - action: help|version|list_plugins|list_runners|switch_runner|execute
    - plugin: plugin name if --plugin specified
    - runner: runner name if --runner specified  
    - command_chain: list of commands/subcommands
    - command_args: dict of command arguments
    """
    i = 0
    plugin = None
    runner = None
    
    # Parse root options until we hit a non-option argument
    while i < len(args):
        arg = args[i]
        
        if arg in ['--help', '-h']:
            return {'action': 'help', 'plugin': plugin, 'runner': runner}
        elif arg == '--version':
            return {'action': 'version'}
        elif arg == '--list-plugins':
            return {'action': 'list_plugins'}
        elif arg == '--list-runners':
            return {'action': 'list_runners'}
        elif arg in ['--plugin', '-p']:
            if i + 1 >= len(args):
                print("Error: --plugin requires a plugin name")
                sys.exit(1)
            plugin = args[i + 1]
            i += 2
        elif arg in ['--runner', '-r']:
            if i + 1 >= len(args):
                print("Error: --runner requires a runner name")
                sys.exit(1)
            runner = args[i + 1]
            
            # If runner is specified, switch to that runner immediately
            return {'action': 'switch_runner', 'runner': runner}
        elif arg.startswith('--'):
            print(f"Error: Unknown root option: {arg}")
            print("Root options must come before commands")
            sys.exit(1)
        else:
            # Hit first non-option argument - this starts the command chain
            break
        
    # Parse command chain and arguments
    command_chain = []
    command_args = {}
    
    # Collect command chain (non-option arguments)
    while i < len(args) and not args[i].startswith('--'):
        command_chain.append(args[i])
        i += 1
    
    # Parse command arguments (--key value pairs)
    while i < len(args):
        if args[i].startswith('--'):
            key = args[i][2:]  # Remove --
            if i + 1 < len(args) and not args[i + 1].startswith('--'):
                command_args[key] = args[i + 1]
                i += 2
            else:
                # Flag argument (no value)
                command_args[key] = True
                i += 1
        else:
            print(f"Error: Unexpected argument: {args[i]}")
            sys.exit(1)
    
    return {
        'action': 'execute',
        'plugin': plugin,
        'runner': runner,
        'command_chain': command_chain,
        'command_args': command_args
    }


def show_main_help(yaapp_engine):
    """Show main yaapp help."""
    print("yaapp - Universal function interface")
    print("")
    print("Usage: yaapp [ROOT_OPTIONS] [COMMAND] [COMMAND_ARGS]")
    print("")
    print("Root Options:")
    print("  --help, -h          Show this help")
    print("  --version           Show version")
    print("  --list-plugins      List available plugins")
    print("  --list-runners      List available runners")
    print("  --plugin NAME       Load specific plugin")
    print("  --runner NAME       Switch to specific runner")
    print("")
    
    # Show available commands (separated by type)
    commands = yaapp_engine.get_commands()
    if commands:
        # Show core commands first (internal yaapp commands)
        core_commands = {name: metadata for name, metadata in commands.items() 
                        if name == "core"}
        if core_commands:
            print("Core Commands:")
            for name, metadata in core_commands.items():
                help_text = yaapp_engine.get_command_help(name)
                print(f"  {name:<15} {help_text}")
                # Show core subcommands if available
                if metadata.get('commands'):
                    for subcmd_name in metadata['commands'].keys():
                        print(f"    {subcmd_name:<13} Core yaapp command")
            print("")
        
        # Show plugin commands (external commands from plugins)
        plugin_commands = {name: metadata for name, metadata in commands.items() 
                          if name != "core"}
        if plugin_commands:
            print("Available Commands:")
            for name, metadata in plugin_commands.items():
                help_text = yaapp_engine.get_command_help(name)
                print(f"  {name:<15} {help_text}")
            print("")
    
    print("Examples:")
    print("  yaapp --help                          # Show this help")
    print("  yaapp --plugin storage --help         # Show storage plugin help") 
    print("  yaapp --plugin storage upload --file data.txt")
    print("  yaapp calculator add --x 5 --y 3")
    print("  yaapp --runner server                 # Start server runner")


def show_contextual_help(yaapp_engine, parsed):
    """Show help based on loaded plugin/runner context."""
    plugin = parsed.get('plugin')
    runner = parsed.get('runner')
    
    if plugin and runner:
        print(f"yaapp with plugin '{plugin}' and runner '{runner}'")
        print("")
        _load_plugin(yaapp_engine, plugin)
        _show_plugin_help(yaapp_engine, plugin)
        print("")
        _show_runner_help(yaapp_engine, runner)
    elif plugin:
        print(f"yaapp with plugin '{plugin}'")
        print("")
        _load_plugin(yaapp_engine, plugin)
        _show_plugin_help(yaapp_engine, plugin)
    elif runner:
        print(f"yaapp with runner '{runner}'")
        print("")
        _show_runner_help(yaapp_engine, runner)
    else:
        show_main_help(yaapp_engine)


def list_plugins(yaapp_engine):
    """List available plugins."""
    print("Available Plugins:")
    print("=" * 40)
    
    plugins = yaapp_engine.get_plugins()
    if plugins:
        for plugin_name in sorted(plugins.keys()):
            print(f"  {plugin_name:<15} - Plugin functionality")
        print("")
        print("Usage:")
        print(f"  yaapp --plugin PLUGIN_NAME --help    # Show plugin help")
        print(f"  yaapp --plugin PLUGIN_NAME COMMAND   # Execute plugin command")
    else:
        print("  No plugins found")


def list_runners(yaapp_engine):
    """List available runners."""
    print("Available Runners:")
    print("=" * 40)
    
    runners = yaapp_engine.get_runners()
    if runners:
        for runner_name, runner_info in sorted(runners.items()):
            help_text = runner_info.get('help', 'Runner available')
            # Clean up help text
            if ':' in help_text:
                help_text = help_text.split(':', 1)[1].strip()
            print(f"  {runner_name:<12} - {help_text}")
        print("")
        print("Usage:")
        print(f"  yaapp --runner RUNNER_NAME           # Switch to runner")
    else:
        print("  No runners found")


def switch_runner(yaapp_engine, runner_name):
    """Switch to a specific runner."""
    # Check if we're trying to switch to the same runner (avoid infinite loop)
    if runner_name == "cli":
        print("Already using CLI runner")
        return
    
    print(f"Switching to {runner_name} runner...")
    
    try:
        # Get runner module directly and run it
        runner_module = yaapp_engine.get_runner_module(runner_name)
        if not runner_module:
            print(f"Error: Runner '{runner_name}' not found")
            return
        
        # Check if runner has run function
        if not hasattr(runner_module, 'run') or not callable(runner_module.run):
            print(f"Error: Runner '{runner_name}' missing run() function")
            return
        
        # Clean sys.argv to remove CLI runner args before switching
        # This prevents the new runner from seeing --runner cli arguments
        original_argv = sys.argv[:]
        try:
            # Remove --runner and runner_name from sys.argv
            cleaned_argv = []
            i = 0
            while i < len(sys.argv):
                if sys.argv[i] in ['--runner', '-r'] and i + 1 < len(sys.argv):
                    # Skip --runner and its argument
                    i += 2
                else:
                    cleaned_argv.append(sys.argv[i])
                    i += 1
            
            sys.argv = cleaned_argv
            
            # Call runner's run function
            runner_module.run(yaapp_engine)
        finally:
            # Restore original argv
            sys.argv = original_argv
        
    except ImportError as e:
        print(f"Error: Failed to load runner '{runner_name}': {e}")
    except Exception as e:
        print(f"Error: Runner execution failed: {e}")


def execute_command(yaapp_engine, parsed):
    """Execute a command with arguments."""
    plugin = parsed.get('plugin')
    command_chain = parsed['command_chain']
    command_args = parsed['command_args']
    
    if not command_chain:
        # No command specified - if plugin was loaded, show help with plugin context
        if plugin:
            _load_plugin(yaapp_engine, plugin)
            show_contextual_help(yaapp_engine, parsed)
        else:
            print("Error: No command specified")
        return
    
    # Load plugin if specified
    if plugin:
        _load_plugin(yaapp_engine, plugin)
    
    # Execute command
    if len(command_chain) == 1:
        # Simple command
        _execute_simple_command(yaapp_engine, command_chain[0], command_args)
    else:
        # Command with subcommands  
        _execute_nested_command(yaapp_engine, command_chain, command_args)


def _load_plugin(yaapp_engine, plugin_name):
    """Load a plugin by name."""
    try:
        plugins = yaapp_engine.get_plugins()
        if plugin_name in plugins:
            yaapp_engine.activate_plugin(plugin_name, {})
        else:
            print(f"Plugin '{plugin_name}' not found")
            print(f"Available plugins: {list(plugins.keys())}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to load plugin '{plugin_name}': {e}")
        sys.exit(1)


def _execute_simple_command(yaapp_engine, command_name, args):
    """Execute a simple command (function or class)."""
    import asyncio
    
    try:
        # Get command metadata to determine type
        commands = yaapp_engine.get_commands()
        if command_name not in commands:
            print(f"Error: Command '{command_name}' not found")
            _suggest_similar_commands(yaapp_engine, command_name)
            return
        
        metadata = commands[command_name]
        
        if metadata['type'] == 'command':
            # Function command
            if args:
                # Command invocation - execute with arguments
                result = asyncio.run(yaapp_engine.execute(command_name, **args))
                _handle_result(result)
            else:
                # Navigation mode - show command info and available options
                help_text = yaapp_engine.get_command_help(command_name)
                print(f"'{command_name}' - {help_text}")
                
                # Show function parameters
                obj = metadata.get('obj')
                if obj:
                    try:
                        import inspect
                        sig = inspect.signature(obj)
                        params = []
                        for param in sig.parameters.values():
                            if param.name == 'yaapp_engine':  # Skip yaapp_engine parameter
                                continue
                            if param.default == inspect.Parameter.empty:
                                params.append(f"--{param.name}")
                            else:
                                params.append(f"[--{param.name}]")
                        
                        if params:
                            param_str = " ".join(params)
                            print(f"Options: {param_str}")
                        else:
                            print("No options required.")
                        
                        print("")
                        print(f"Usage: yaapp {command_name} {' '.join(params) if params else ''}")
                    except (ValueError, TypeError):
                        print(f"Usage: yaapp {command_name} [options...]")
        elif metadata['type'] == 'group':
            # Class command - show available methods
            print(f"'{command_name}' is a class with the following methods:")
            methods = metadata.get('commands', {})
            for method_name, method_info in methods.items():
                help_text = yaapp_engine.get_method_help(command_name, method_name)
                print(f"  {method_name:<15} {help_text}")
                
                # Show method parameters in navigation mode
                params = method_info.get('params', {})
                if params:
                    param_strings = []
                    for param_name, param_info in params.items():
                        if param_name == 'yaapp_engine':  # Skip yaapp_engine parameter
                            continue
                        if param_info.get('required', False):
                            param_strings.append(f"--{param_name}")
                        else:
                            param_strings.append(f"[--{param_name}]")
                    if param_strings:
                        param_str = " ".join(param_strings)
                        print(f"    {'':<13} Options: {param_str}")
            print("")
            print(f"Usage: yaapp {command_name} METHOD_NAME [args...]")
        
    except Exception as e:
        print(f"Error executing command: {e}")


def _execute_nested_command(yaapp_engine, command_chain, args):
    """Execute nested command (class method)."""
    import asyncio
    
    try:
        class_name = command_chain[0]
        method_name = command_chain[1]
        
        if args:
            # Command invocation - execute with arguments
            result = asyncio.run(yaapp_engine.execute(f"{class_name}.{method_name}", **args))
            
            if result.is_ok():
                value = result.unwrap()
                if value is not None:
                    print(f"Result: {value}")
            else:
                print(f"Error: {result.as_error}")
        else:
            # Navigation mode - show method info and available options
            commands = yaapp_engine.get_commands()
            if class_name in commands:
                class_metadata = commands[class_name]
                methods = class_metadata.get('commands', {})
                if method_name in methods:
                    method_info = methods[method_name]
                    help_text = yaapp_engine.get_method_help(class_name, method_name)
                    print(f"'{class_name} {method_name}' - {help_text}")
                    
                    # Show method parameters
                    params = method_info.get('params', {})
                    param_strings = []
                    
                    if params:
                        for param_name, param_info in params.items():
                            if param_name == 'yaapp_engine':  # Skip yaapp_engine parameter
                                continue
                            if param_info.get('required', False):
                                param_strings.append(f"--{param_name}")
                            else:
                                param_strings.append(f"[--{param_name}]")
                    
                    if param_strings:
                        param_str = " ".join(param_strings)
                        print(f"Options: {param_str}")
                    else:
                        print("No options required.")
                    
                    print("")
                    param_usage = " ".join(param_strings) if param_strings else ""
                    print(f"Usage: yaapp {class_name} {method_name} {param_usage}")
                else:
                    print(f"Error: Method '{method_name}' not found in '{class_name}'")
            else:
                print(f"Error: Command '{class_name}' not found")
            
    except Exception as e:
        print(f"Error executing command: {e}")


def _handle_result(result):
    """Handle command execution result."""
    if result.is_ok():
        value = result.unwrap()
        if value is not None:
            print(f"Result: {value}")
    else:
        print(f"Error: {result.as_error}")


def _suggest_similar_commands(yaapp_engine, command_name):
    """Suggest similar commands when command not found."""
    commands = yaapp_engine.get_commands()
    similar = []
    
    for name in commands.keys():
        if name != "core" and command_name.lower() in name.lower():
            similar.append(name)
    
    if similar:
        print(f"Did you mean: {', '.join(similar)}?")
    else:
        print("Use 'yaapp --help' to see available commands")


def _show_plugin_help(yaapp_engine, plugin_name):
    """Show help for a specific plugin."""
    commands = yaapp_engine.get_commands()
    
    # Show core commands
    core_commands = {name: metadata for name, metadata in commands.items() 
                    if name == "core"}
    if core_commands:
        print("Core Commands:")
        for name, metadata in core_commands.items():
            help_text = yaapp_engine.get_command_help(name)
            print(f"  {name:<15} {help_text}")
            # Show core subcommands
            if metadata.get('commands'):
                for subcmd_name in metadata['commands'].keys():
                    print(f"    {subcmd_name:<13} Core yaapp command")
        print("")
    
    # Show plugin commands
    plugin_commands = {name: metadata for name, metadata in commands.items() 
                      if name != "core"}
    
    if plugin_commands:
        print(f"Plugin '{plugin_name}' commands:")
        for name, metadata in plugin_commands.items():
            help_text = yaapp_engine.get_command_help(name)
            print(f"  {name:<15} {help_text}")
    else:
        print(f"No plugin commands found for plugin '{plugin_name}'")


def _show_runner_help(yaapp_engine, runner_name):
    """Show help for a specific runner."""
    runners = yaapp_engine.get_runners()
    if runner_name in runners:
        runner_info = runners[runner_name]
        help_text = runner_info.get('help', f"Runner: {runner_name}")
        print(f"Runner '{runner_name}': {help_text}")
    else:
        print(f"Runner '{runner_name}' not found")


