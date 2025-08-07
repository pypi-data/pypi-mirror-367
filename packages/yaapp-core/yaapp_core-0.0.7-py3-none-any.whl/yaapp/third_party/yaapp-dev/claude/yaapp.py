"""
YAPP - Yet Another Python Package
A library bridging FastAPI and CLI interfaces inspired by fast-agent
"""

import inspect
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union


class YApp:
    """
    Main YAPP application class that bridges CLI and web interfaces.

    Inspired by fast-agent's architecture, provides a single entry point
    that can expose functions/classes and run in different contexts.
    """

    def __init__(self):
        self._registry: Dict[str, Any] = {}
        self._config: Optional[Dict[str, Any]] = None

    def expose(
        self, item: Union[Callable, type, Dict[str, Any]]
    ) -> Union[Callable, type, None]:
        """
        Expose functions, classes, or dictionary trees for CLI/web interfaces.

        Can be used as:
        1. Decorator: @yapp.expose (for functions/classes)
        2. Method call: yapp.expose({...}) (for dictionary trees)

        Args:
            item: Function, class, or dictionary tree to expose

        Returns:
            The original item if used as decorator, None if method call
        """
        if inspect.isfunction(item) or inspect.isclass(item):
            # Decorator usage - register and return the item
            name = getattr(item, "__name__", str(item))
            self._register_item(name, item)
            return item

        elif isinstance(item, dict):
            # Method call usage - register the tree
            self._register_tree(item)
            return None

        else:
            # Other callable - treat as decorator
            name = getattr(item, "__name__", str(item))
            self._register_item(name, item)
            return item

    def _register_item(self, name: str, item: Any) -> None:
        """Register a single item in the registry."""
        self._registry[name] = item

    def _register_tree(self, tree: Dict[str, Any], prefix: str = "") -> None:
        """Register a dictionary tree in the registry."""
        for key, value in tree.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                # Nested dictionary - recurse
                self._register_tree(value, full_key)
            else:
                # Leaf node - register the item
                self._registry[full_key] = value

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from yaapp.yaml and yapp.secrets.yaml."""
        if self._config is not None:
            return self._config

        config = {}

        # Try to load yapp.yaml
        config_path = Path("yapp.yaml")
        if config_path.exists():
            try:
                import yaml

                with open(config_path, "r") as f:
                    config = yaml.safe_load(f) or {}
            except ImportError:
                print("Warning: PyYAML not installed. Cannot load yapp.yaml")
            except Exception as e:
                print(f"Warning: Error loading yapp.yaml: {e}")

        # Try to load yapp.secrets.yaml and merge
        secrets_path = Path("yapp.secrets.yaml")
        if secrets_path.exists():
            try:
                import yaml

                with open(secrets_path, "r") as f:
                    secrets = yaml.safe_load(f) or {}
                    # Merge secrets into config (secrets take precedence)
                    config = self._merge_config(config, secrets)
            except ImportError:
                pass  # Already warned about PyYAML
            except Exception as e:
                print(f"Warning: Error loading yapp.secrets.yaml: {e}")

        self._config = config
        return config

    def _merge_config(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge configuration dictionaries, with override taking precedence."""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value

        return result

    def _detect_execution_mode(self) -> str:
        """
        Detect execution mode based on configuration and context.

        Priority (following fast-agent patterns):
        1. yapp.yaml configuration
        2. Environment variables
        3. Command line arguments
        4. Default behavior
        """
        config = self._load_config()

        # Check configuration file
        execution_mode = config.get("execution_mode", "auto")
        if execution_mode in ["cli", "web"]:
            return execution_mode

        # Check environment variables
        import os

        if os.getenv("YAPP_MODE") == "web" or os.getenv("PORT"):
            return "web"
        if os.getenv("YAPP_MODE") == "cli":
            return "cli"

        # Check command line arguments
        if len(sys.argv) > 1:
            # Has CLI arguments - assume CLI mode
            return "cli"

        # Default to CLI for now
        return "cli"

    def _run_cli(self) -> None:
        """Run in CLI mode using Click/Typer."""
        print("CLI mode detected")
        print(f"Available functions: {list(self._registry.keys())}")

        # TODO: Implement actual CLI generation using Click/Typer
        # For now, just show what would be available
        if not self._registry:
            print(
                "No functions exposed. Use @yapp.expose or yapp.expose({...}) to expose functionality."
            )
            return

        # Simple demo implementation
        if len(sys.argv) > 1:
            func_name = sys.argv[1]
            if func_name in self._registry:
                func = self._registry[func_name]
                print(f"Would execute: {func_name}")
                print(f"Function: {func}")
                # TODO: Parse arguments and call function
            else:
                print(f"Unknown function: {func_name}")
                print(f"Available: {list(self._registry.keys())}")
        else:
            print("Usage: python script.py <function_name> [args...]")

    def _run_web(self) -> None:
        """Run in web mode using FastAPI."""
        print("Web mode detected")
        print(f"Available functions: {list(self._registry.keys())}")

        config = self._load_config()
        server_config = config.get("server", {})
        host = server_config.get("host", "127.0.0.1")
        port = server_config.get("port", 8000)

        print(f"Would start web server on {host}:{port}")

        # TODO: Implement actual FastAPI server generation
        # For now, just show what would be available
        if not self._registry:
            print(
                "No functions exposed. Use @yapp.expose or yapp.expose({...}) to expose functionality."
            )
            return

        print("Would create endpoints:")
        for name, func in self._registry.items():
            print(f"  POST /{name}")

    def run(self) -> None:
        """
        Context-aware execution - determines mode and runs accordingly.

        This is the single entry point that users call.
        """
        mode = self._detect_execution_mode()

        if mode == "web":
            self._run_web()
        else:  # mode == 'cli' or default
            self._run_cli()
