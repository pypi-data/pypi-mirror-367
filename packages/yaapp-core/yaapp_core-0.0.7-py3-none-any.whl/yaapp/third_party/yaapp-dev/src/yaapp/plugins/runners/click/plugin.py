"""
Click runner plugin for yaapp.
Provides the default CLI interface with interactive shell capabilities.
"""

import sys
# Import will be done dynamically to avoid circular imports

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False
    click = None

from yaapp import yaapp


@yaapp.expose("click")
class ClickRunner:
    """Click-based CLI runner - default runner for yaapp applications."""
    
    def __init__(self, config=None):
        """Initialize Click runner with optional configuration."""
        self.config = config or {}    
    def help(self) -> str:
        """Return Click runner-specific help text."""
        return """
🖱️ CLICK CLI RUNNER HELP:
  --verbose       Enable verbose output
  --quiet         Suppress output
  --interactive   Start interactive shell mode
        """
    
    def run(self, app_instance, **kwargs):
        """Execute the Click runner with the app instance."""
        if not HAS_CLICK:
            print("click not available. Install with: pip install click")
            return
        
        # Extract configuration with CLI args taking priority
        verbose = kwargs.get('verbose', self.config.get('verbose', False))
        quiet = kwargs.get('quiet', self.config.get('quiet', False))
        interactive = kwargs.get('interactive', self.config.get('interactive', False))
        
        # Check if interactive mode is requested
        if interactive:
            self._run_interactive(verbose, quiet)
        else:
            self._run_standard(verbose, quiet)
    
    def _run_standard(self, verbose=False, quiet=False):
        """Run standard Click CLI mode."""
        # Create a simple CLI with reflected commands (not hierarchical)
        cli = self._create_simple_cli(verbose, quiet)
        if cli:
            # Execute the CLI normally
            cli()
    
    def _create_simple_cli(self, verbose=False, quiet=False):
        """Create a simple Click CLI with reflected commands only."""
        if not HAS_CLICK:
            return None
        
        from yaapp.reflection import CommandReflector
        
        @click.group(invoke_without_command=True)
        @click.pass_context
        def cli(ctx):
            """YApp CLI with automatic function and class reflection."""
            if verbose and not quiet:
                click.echo("Verbose mode enabled")
            if ctx.invoked_subcommand is None:
                click.echo(ctx.get_help())
        
        # Add reflected commands
        command_reflector = CommandReflector(yaapp)
        command_reflector.add_reflected_commands(cli)
        
        return cli
    
    def _run_interactive(self, verbose=False, quiet=False):
        """Run interactive Click shell mode."""
        # Create a simple CLI with reflected commands
        cli = self._create_simple_cli(verbose, quiet)
        if cli:
            # Start click in interactive mode
            old_argv = sys.argv
            try:
                if not quiet:
                    print("YApp Interactive Shell (Click)")
                    print("Use --help for any command to see options")
                    print("Available commands: help, plus all exposed functions")
                    print()

                while True:
                    try:
                        user_input = input(f"{yaapp._get_app_name()}> ").strip()
                        if not user_input:
                            continue

                        if user_input.lower() in ["exit", "quit"]:
                            print("Goodbye!")
                            break

                        # Parse command and execute through click
                        sys.argv = [yaapp._get_app_name()] + user_input.split()
                        try:
                            cli()
                        except SystemExit:
                            # Click calls sys.exit(), we want to continue the loop
                            pass
                        except Exception as e:
                            print(f"Error: {e}")

                    except (EOFError, KeyboardInterrupt):
                        print("\\nGoodbye!")
                        break
            finally:
                sys.argv = old_argv