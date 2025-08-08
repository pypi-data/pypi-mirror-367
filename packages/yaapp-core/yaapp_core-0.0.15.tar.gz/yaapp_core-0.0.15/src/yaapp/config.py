"""
Simple configuration system for yaapp-core.

Provides async configuration loading with priority-based hierarchy:
1. kwargs dict (highest priority)
2. environment variables
3. config file from current directory
4. config file from project (git repo root)
5. config file from $HOME/.config/yaapp/yaapp.yaml (XDG standard)
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Union

from .result import Ok, Result
from .config_node import ConfigNode


class Config:
    """Simple configuration class with priority-based loading."""

    def __init__(self):
        """Initialize empty configuration - constructor does nothing."""
        self._config_data: Dict[str, Any] = {}
        self._root_node: Optional[ConfigNode] = None

    async def load_config(self, path: Optional[str] = None, **kwargs) -> Result[bool]:
        """Load configuration with priority hierarchy.

        Priority order (highest to lowest):
        1. kwargs dict
        2. environment variables
        3. config file from current directory
        4. config file from project (git repo root)
        5. config file from $HOME/.config/yaapp/yaapp.yaml

        Args:
            path: Optional explicit config file path
            **kwargs: Configuration overrides (highest priority)

        Returns:
            Result[bool]: Ok(True) if successful, Err with error message if failed
        """
        config = {}

        # Priority 5: XDG config file ($HOME/.config/yaapp/yaapp.yaml)
        xdg_result = await self._load_xdg_config()
        if xdg_result.is_ok():
            xdg_config = xdg_result.unwrap()
            self._merge_config(config, xdg_config)

        # Priority 4: Project root config file
        project_result = await self._load_project_config()
        if project_result.is_ok():
            project_config = project_result.unwrap()
            self._merge_config(config, project_config)

        # Priority 3: Current directory config file
        current_result = await self._load_current_directory_config()
        if current_result.is_ok():
            current_config = current_result.unwrap()
            self._merge_config(config, current_config)

        # Explicit path overrides current directory
        if path:
            file_result = await self._load_config_file(path)
            if file_result.is_ok():
                file_config = file_result.unwrap()
                self._merge_config(config, file_config)

        # Priority 2: Environment variables
        env_result = await self._load_env_config()
        if env_result.is_ok():
            env_config = env_result.unwrap()
            self._merge_config(config, env_config)

        # Priority 1: kwargs (highest priority)
        if kwargs:
            self._merge_config(config, kwargs)

        self._config_data = config
        # Reset root node to force rebuild with new data
        self._root_node = None
        return Ok(True)

    async def get(self, path: str) -> Result[Any]:
        """Get configuration value by dot notation path using hierarchical inheritance.
        
        Args:
            path: Dot notation path (e.g., 'server.host', 'database.port')
            
        Returns:
            Result[Any]: Ok with the value if found, Err if path not found
        """
        if not path:
            return Result.error("Empty path not allowed")
            
        parts = path.split(".")
        current_node = self.root
        
        # Navigate through all parts except the last
        for part in parts[:-1]:
            result = current_node.get_attr(part)
            if result.is_err():
                return Result.error("path not found")
            
            value = result.unwrap()
            if not isinstance(value, ConfigNode):
                return Result.error("path not found")
            current_node = value
        
        # Get the final value
        final_key = parts[-1]
        result = current_node.get_attr(final_key)
        if result.is_err():
            return Result.error("path not found")
            
        value = result.unwrap()
        
        # If it's an auto-instantiated empty ConfigNode, treat as not found
        if isinstance(value, ConfigNode) and not value._data:
            return Result.error("path not found")
            
        # Return the actual value (dict/list/scalar), not ConfigNode
        if isinstance(value, ConfigNode):
            return Ok(value.to_dict())
        else:
            return Ok(value)

    async def set(self, path: str, value: Any) -> Result[bool]:
        """Set configuration value by dot notation path for runtime injection.
        
        Args:
            path: Dot notation path (e.g., 'server.host', 'database.port')
            value: Value to set
            
        Returns:
            Result[bool]: Ok(True) if successful, Err with error message if failed
        """
        if not path:
            return Result.error("Empty path not allowed")
            
        parts = path.split(".")
        current_node = self.root
        
        # Navigate through all parts except the last, creating nodes as needed
        for part in parts[:-1]:
            result = current_node.get_attr(part)
            if result.is_err():
                return Result.error(f"Failed to navigate path: {result.as_error}")
            
            node_value = result.unwrap()
            if not isinstance(node_value, ConfigNode):
                return Result.error(f"Cannot set nested value - {part} is not a section")
            current_node = node_value
        
        # Set the final value in the node's data
        final_key = parts[-1]
        current_node._data[final_key] = value
        return Ok(True)

    @property
    def root(self) -> ConfigNode:
        """Get the hierarchical configuration root node with lazy initialization."""
        if self._root_node is None:
            self._root_node = ConfigNode(self._config_data)
        return self._root_node

    async def _load_xdg_config(self) -> Result[Dict[str, Any]]:
        """Load config from XDG standard location: $HOME/.config/yaapp/yaapp.yaml"""
        home = os.path.expanduser("~")
        xdg_path = Path(home) / ".config" / "yaapp" / "yaapp.yaml"

        if xdg_path.exists():
            return await self._load_config_file(str(xdg_path))
        return Ok({})

    async def _load_project_config(self) -> Result[Dict[str, Any]]:
        """Load config from project root (git repo root)."""
        # Find git repo root by looking for .git directory
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                # Found git root, look for config file
                for filename in ["yaapp.yaml", "yaapp.yml"]:
                    config_path = current / filename
                    if config_path.exists():
                        return await self._load_config_file(str(config_path))
                break
            current = current.parent
        return Ok({})

    async def _load_current_directory_config(self) -> Result[Dict[str, Any]]:
        """Load config from current directory."""
        for filename in ["yaapp.yaml", "yaapp.yml"]:
            config_path = Path(filename)
            if config_path.exists():
                return await self._load_config_file(str(config_path))
        return Ok({})

    async def _load_config_file(self, file_path: str) -> Result[Dict[str, Any]]:
        """Load configuration from YAML file.

        Args:
            file_path: Path to config file

        Returns:
            Result[Dict]: Ok with config data or Err with error message
        """
        try:
            config_path = Path(file_path)
            if not config_path.exists():
                return Ok({})

            # Only support YAML files
            if config_path.suffix.lower() not in [".yaml", ".yml"]:
                return Result.error(
                    f"Only YAML files supported, got: {config_path.suffix}"
                )

            # Import yaml only when needed
            try:
                import yaml
            except ImportError:
                return Result.error(
                    "PyYAML not installed. Install with: pip install PyYAML"
                )

            with open(config_path, "r") as f:
                data = yaml.safe_load(f) or {}

            # Apply environment variable substitution
            data = self._substitute_env_variables(data)
            return Ok(data)

        except (IOError, OSError) as e:
            return Result.error(f"Failed to load config file {file_path}: {str(e)}")
        except Exception as e:
            # Catch yaml.YAMLError and other parsing errors
            return Result.error(f"Failed to parse config file {file_path}: {str(e)}")

    async def _load_env_config(self) -> Result[Dict[str, Any]]:
        """Load configuration from YAAPP_* environment variables.

        Converts YAAPP_SECTION_KEY to section.key structure.

        Returns:
            Result[Dict]: Ok with config data from environment variables
        """
        config = {}

        for key, value in os.environ.items():
            if key.startswith("YAAPP_"):
                # YAAPP_SERVER_HOST -> server.host
                parts = key[6:].lower().split("_")  # Remove YAAPP_ prefix
                if len(parts) >= 2:
                    section = parts[0]
                    setting = "_".join(parts[1:])

                    if section not in config:
                        config[section] = {}

                    # Parse and type-convert common values
                    parsed_value = self._parse_env_value(value)
                    config[section][setting] = parsed_value

        return Ok(config)

    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value with type conversion.

        Args:
            value: Raw environment variable value

        Returns:
            Parsed value with appropriate type
        """
        # Handle comma-separated lists (unless escaped)
        if "," in value and not value.startswith("\\"):
            return [v.strip() for v in value.split(",")]

        # Remove escape character if present
        if value.startswith("\\"):
            value = value[1:]

        # Convert common boolean strings
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        elif value.lower() in ("false", "no", "0", "off"):
            return False

        # Try to convert to int
        try:
            return int(value)
        except ValueError:
            pass

        # Try to convert to float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _substitute_env_variables(self, data: Union[Dict, list, str, Any]) -> Any:
        """Recursively substitute environment variables in configuration data.

        Supports ${VAR:default} syntax.

        Args:
            data: Configuration data to process

        Returns:
            Data with environment variables substituted
        """
        if isinstance(data, str):
            # Pattern to match ${VAR:default} or ${VAR}
            pattern = r"\$\{([^}:]+)(?::([^}]*))?\}"

            def replace_var(match):
                var_name = match.group(1)
                default_value = match.group(2) if match.group(2) is not None else ""
                return os.getenv(var_name, default_value)

            return re.sub(pattern, replace_var, data)

        elif isinstance(data, dict):
            return {
                key: self._substitute_env_variables(value)
                for key, value in data.items()
            }

        elif isinstance(data, list):
            return [self._substitute_env_variables(item) for item in data]

        else:
            return data

    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Merge override configuration into base configuration.

        Args:
            base: Base configuration dictionary (modified in-place)
            override: Override configuration dictionary
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                # Recursive merge for nested dictionaries
                self._merge_config(base[key], value)
            else:
                # Override value
                base[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary.

        Returns:
            Complete configuration dictionary
        """
        return self._config_data.copy()

