"""
Enterprise-grade configuration system for yaapp with environment variables and secrets support.
"""

import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .config_node import ConfigNode


class ConfigSource(Enum):
    """Configuration source priority order."""

    ENVIRONMENT = "environment"
    CONFIG_FILE = "config_file"
    SECRETS_FILE = "secrets_file"
    DEFAULT = "default"


def substitute_env_variables(data: Union[Dict, List, str, Any]) -> Any:
    """
    Recursively substitute environment variables in configuration data.
    Supports ${VAR:default} syntax.
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
        return {key: substitute_env_variables(value) for key, value in data.items()}

    elif isinstance(data, list):
        return [substitute_env_variables(item) for item in data]

    else:
        return data


def parse_env_value(value: str):
    """Parse env value: if has comma, split to list unless escaped."""
    if ',' in value and not value.startswith('\\'):
        return [v.strip() for v in value.split(',')]
    return value.lstrip('\\')  # Remove escape if present

def load_config_from_env() -> Dict[str, Any]:
    """Load config from YAAPP_XXXX_YYY env vars into xxx.yyy structure."""
    config = {}
    
    for key, value in os.environ.items():
        if key.startswith('YAAPP_'):
            # YAAPP_SERVER_HOST -> server.host
            parts = key[6:].lower().split('_')  # Remove YAAPP_ prefix
            if len(parts) >= 2:
                section = parts[0]  # server, security, logging
                setting = '_'.join(parts[1:])  # host, allowed_origins
                
                if section not in config:
                    config[section] = {}
                
                # Parse value
                parsed_value = parse_env_value(value)
                
                # Type conversion
                if setting in ['port', 'workers', 'timeout', 'rate_limit', 'max_size', 'backup_count']:
                    parsed_value = int(parsed_value)
                elif setting in ['reload', 'enable_cors']:
                    parsed_value = str(parsed_value).lower() == 'true'
                
                config[section][setting] = parsed_value
    
    return config


class YaappConfig:
    """Simple config container - no more enterprise garbage."""
    
    def __init__(self):
        # Default config
        self.config = {
            'server': {
                'host': 'localhost',
                'port': 8000,
                'reload': False,
                'workers': 1,
                'timeout': 30
            },
            'security': {
                'api_key': None,
                'secret_key': None,
                'allowed_origins': ['*'],
                'rate_limit': 1000,
                'enable_cors': True
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': None,
                'max_size': 10_000_000,
                'backup_count': 5
            }
        }
        
        # Plugin configurations
        self.plugins = {}
        self.discovered_sections = {}
    
    @property
    def server(self):
        return self.config['server']
    
    @property
    def security(self):
        return self.config['security']
    
    @property
    def logging(self):
        return self.config['logging']

    def __post_init__(self):
        """Initialize hierarchical configuration after dataclass creation."""
        self._root_node: Optional[ConfigNode] = None
        self._raw_config_data: Dict[str, Any] = {}

    def load(self, config_file: Optional[Union[str, Path]] = None) -> 'Result[bool]':
        """Load configuration with proper hierarchy: defaults -> file -> env."""
        from .result import Result, Ok
        
        # 1. Defaults already loaded in __init__
        
        # 2. Load from config file (overrides defaults)
        if config_file:
            result = self._load_from_file(config_file)
            if result.is_err():
                return result
        else:
            # Auto-find config file
            auto_file = self._find_config_file()
            if auto_file:
                result = self._load_from_file(auto_file)
                if result.is_err():
                    return result
        
        # 3. Load from env vars (overrides everything)
        env_config = load_config_from_env()
        self._merge_config(self.config, env_config)
        
        return Ok(True)
    
    def _find_config_file(self) -> Optional[str]:
        """Find YAML config file."""
        for filename in ['yaapp.yaml', 'yaapp.yml']:
            if Path(filename).exists():
                return filename
        return None
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Merge override config into base config."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)  # Recursive merge
            else:
                base[key] = value  # Override

    @property
    def root(self) -> ConfigNode:
        """Get the hierarchical configuration root node."""
        if self._root_node is None:
            self._create_hierarchical_config()
        return self._root_node

    def get_plugin_config(self, plugin_name: str) -> ConfigNode:
        """Get plugin configuration with inheritance."""
        result = self.root.get_attr(plugin_name)
        if result.is_ok():
            return result.unwrap()
        else:
            # Return empty ConfigNode for missing plugin config
            return ConfigNode({}, parent=self.root, path=plugin_name)

    def _create_hierarchical_config(self) -> None:
        """Create hierarchical configuration from current state."""
        # Build complete config data including all sections
        config_data = {
            "server": {
                "host": self.server.host,
                "port": self.server.port,
                "reload": self.server.reload,
                "workers": self.server.workers,
                "timeout": self.server.timeout,
            },
            "security": {
                "allowed_origins": self.security.allowed_origins,
                "rate_limit": self.security.rate_limit,
                "enable_cors": self.security.enable_cors,
                # Include secrets if available
                **(
                    {
                        "api_key": self.security.api_key,
                        "secret_key": self.security.secret_key,
                    }
                    if self.security.api_key or self.security.secret_key
                    else {}
                ),
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file": self.logging.file,
                "max_size": self.logging.max_size,
                "backup_count": self.logging.backup_count,
            },
            **self.custom,
            **self.discovered_sections,
        }

        # Store raw data and create root node
        self._raw_config_data = config_data
        self._root_node = ConfigNode(config_data)

    def _load_from_file(self, config_file: Union[str, Path]) -> 'Result[bool]':
        """Load configuration from YAML file."""
        from .result import Result, Ok
        
        try:
            # Import yaml where it's used
            try:
                import yaml
            except ImportError:
                return Result.error("PyYAML not installed. Install with: pip install PyYAML")
            
            config_path = Path(config_file)
            if not config_path.exists():
                return Ok(True)  # Not an error if file doesn't exist

            # Only support YAML files
            if config_path.suffix.lower() not in [".yaml", ".yml"]:
                return Result.error(f"Only YAML files are supported, got: {config_path.suffix}")

            with open(config_path, "r") as f:
                data = yaml.safe_load(f)

            if not data:
                return Ok(True)

            # Apply environment variable substitution
            data = substitute_env_variables(data)

            # Merge into config
            self._merge_config(self.config, data)
            
            return Ok(True)

        except (IOError, TypeError) as e:
            return Result.error(f"Failed to load config file {config_file}: {str(e)}")
        except Exception as e:
            # This will catch yaml.YAMLError and other yaml-related errors
            return Result.error(f"Failed to load config file {config_file}: {str(e)}")
            
            # Only support YAML files
            if config_path.suffix.lower() not in [".yaml", ".yml"]:
                return Result.error(f"Only YAML files are supported, got: {config_path.suffix}")

            with open(config_path, "r") as f:
                data = yaml.safe_load(f)

            if not data:
                return Ok(True)

            # Apply environment variable substitution
            data = substitute_env_variables(data)

            # Merge into config
            self._merge_config(self.config, data)
            
            return Ok(True)

        except (IOError, json.JSONDecodeError, yaml.YAMLError, TypeError) as e:
            return Result.error(f"Failed to load config file {config_file}: {str(e)}")

    def _discover_and_configure_plugins(self, config_data: Dict[str, Any]) -> None:
        """Discover and configure plugins based on configuration sections."""
        # Reserved sections that are not plugins
        reserved_sections = {
            "server",
            "security",
            "logging",
            "custom",
            "app",
            "execution_mode",
            "auto_sampling",
            "execution_engine",
            "cli",
            "environment",
        }

        # Find potential plugin sections
        plugin_sections = [
            key for key in config_data.keys() if key not in reserved_sections
        ]

        if not plugin_sections:
            return

        # Import discovery system
        from .plugin_discovery import PluginDiscovery

        discovery = PluginDiscovery()

        # Discover available plugins
        discovered_plugins = discovery.discover_plugins(plugin_sections)

        # Configure discovered plugins
        for section_name, plugin_imported in discovered_plugins.items():
            if section_name in config_data:
                try:
                    # Store plugin configuration
                    plugin_config = config_data[section_name]
                    self.discovered_sections[section_name] = plugin_config

                    # Plugin is already registered via @yaapp.expose decorator during import
                    # Just store the config for reference
                    self.plugins[section_name] = {
                        "imported": plugin_imported,
                        "config": plugin_config,
                    }

                    print(f"✅ Loaded plugin: {section_name}")

                except (AttributeError, TypeError) as e:
                    # Log warning but continue with other plugins
                    print(f"Warning: Failed to configure plugin '{section_name}': {e}")
                    continue

        # Warn about sections that couldn't be matched to plugins
        unmatched = set(plugin_sections) - set(discovered_plugins.keys())
        for section in unmatched:
            # Store unmatched sections in discovered_sections so they're available in hierarchical config
            if section in config_data:
                self.discovered_sections[section] = config_data[section]
            print(f"Warning: No plugin found for configuration section '{section}'")
            print(f"  Consider installing plugin or removing section from config")

    def register_discovered_plugins(self, app_instance):
        """Register discovered plugins with the app instance."""
        # Plugins are registered via @yaapp.expose decorator during import as classes
        # We need to instantiate them with their configuration
        for section_name, plugin_info in self.plugins.items():
            if isinstance(plugin_info, dict) and plugin_info.get("imported"):
                try:
                    # Get the plugin class from the registry
                    plugin_result = app_instance.get_registry_item(section_name)
                    if plugin_result.is_ok():
                        plugin_class = plugin_result.unwrap()

                        # Check if it's already an instance or still a class
                        if isinstance(plugin_class, type):
                            # It's a class, instantiate it with configuration
                            plugin_config = plugin_info.get("config", {})
                            plugin_instance = plugin_class(plugin_config)

                            # Set the yaapp reference
                            plugin_instance.yaapp = app_instance

                            # Replace the class with the instance in the registry
                            exposer = app_instance._registry[section_name][1]
                            app_instance._registry[section_name] = (
                                plugin_instance,
                                exposer,
                            )

                            # Call the exposer's expose method on the new instance to trigger expose_to_registry
                            if hasattr(exposer, "expose"):
                                exposer.expose(
                                    plugin_instance, section_name, custom=True
                                )

                            print(
                                f"🔗 Plugin ready: {section_name} (instantiated with config)"
                            )
                        else:
                            # Already an instance
                            print(
                                f"🔗 Plugin ready: {section_name} (already instantiated)"
                            )
                    else:
                        print(f"Warning: Plugin '{section_name}' not found in registry")
                except (AttributeError, TypeError) as e:
                    print(
                        f"Warning: Failed to instantiate plugin '{section_name}': {e}"
                    )
            else:
                print(f"Warning: Plugin '{section_name}' was not properly imported")

    # Plugin methods are exposed by @yaapp.expose decorator, instances created in register_discovered_plugins

    def _load_secrets_from_file(self, secrets_file: Union[str, Path]) -> None:
        """Load secrets from encrypted/secure file."""
        secrets_path = Path(secrets_file)

        if not secrets_path.exists():
            return

        try:
            with open(secrets_path, "r") as f:
                if secrets_path.suffix.lower() in [".yaml", ".yml"]:
                    if not HAS_YAML:
                        print(
                            "Warning: YAML secrets file found but PyYAML not installed"
                        )
                        return
                    try:
                        secrets = yaml.safe_load(f)
                    except yaml.YAMLError as e:
                        print(
                            f"Warning: Invalid YAML in secrets file {secrets_file}: {e}"
                        )
                        return
                else:
                    try:
                        secrets = json.load(f)
                    except json.JSONDecodeError as e:
                        print(
                            f"Warning: Invalid JSON in secrets file {secrets_file}: {e}"
                        )
                        return

            # Apply environment variable substitution to secrets
            secrets = substitute_env_variables(secrets)

            # Load only secret values
            if "security" in secrets:
                if "api_key" in secrets["security"]:
                    self.security.api_key = secrets["security"]["api_key"]
                if "secret_key" in secrets["security"]:
                    self.security.secret_key = secrets["security"]["secret_key"]

        except (IOError, json.JSONDecodeError, yaml.YAMLError, TypeError) as e:
            print(f"Warning: Failed to load secrets file {secrets_file}: {e}")

    def _load_from_environment(self, prefix: str = "YAAPP_") -> None:
        """Load configuration from environment variables (only overrides existing values)."""
        # Apply environment overrides to existing config (don't replace with defaults)
        server_prefix = f"{prefix}SERVER_"
        security_prefix = f"{prefix}SECURITY_"
        log_prefix = f"{prefix}LOG_"

        # Override server config if environment variables exist
        for env_var, attr_name in [
            (f"{server_prefix}HOST", "host"),
            (f"{server_prefix}PORT", "port"),
            (f"{server_prefix}RELOAD", "reload"),
            (f"{server_prefix}WORKERS", "workers"),
            (f"{server_prefix}TIMEOUT", "timeout"),
        ]:
            if env_var in os.environ:
                value = os.environ[env_var]
                if attr_name in ["port", "workers", "timeout"]:
                    value = int(value)
                elif attr_name == "reload":
                    value = value.lower() == "true"
                setattr(self.server, attr_name, value)

        # Override security config if environment variables exist
        for env_var, attr_name in [
            (f"{security_prefix}API_KEY", "api_key"),
            (f"{security_prefix}SECRET_KEY", "secret_key"),
            (f"{security_prefix}ALLOWED_ORIGINS", "allowed_origins"),
            (f"{security_prefix}RATE_LIMIT", "rate_limit"),
            (f"{security_prefix}ENABLE_CORS", "enable_cors"),
        ]:
            if env_var in os.environ:
                value = os.environ[env_var]
                if attr_name == "allowed_origins":
                    value = (
                        [origin.strip() for origin in value.split(",")]
                        if value != "*"
                        else ["*"]
                    )
                elif attr_name == "rate_limit":
                    value = int(value)
                elif attr_name == "enable_cors":
                    value = value.lower() == "true"
                setattr(self.security, attr_name, value)

        # Override logging config if environment variables exist
        for env_var, attr_name in [
            (f"{log_prefix}LEVEL", "level"),
            (f"{log_prefix}FORMAT", "format"),
            (f"{log_prefix}FILE", "file"),
            (f"{log_prefix}MAX_SIZE", "max_size"),
            (f"{log_prefix}BACKUP_COUNT", "backup_count"),
        ]:
            if env_var in os.environ:
                value = os.environ[env_var]
                if attr_name in ["max_size", "backup_count"]:
                    value = int(value)
                setattr(self.logging, attr_name, value)

        # Load custom environment variables
        for key, value in os.environ.items():
            if key.startswith(f"{prefix}CUSTOM_"):
                custom_key = key[len(f"{prefix}CUSTOM_") :].lower()
                self.custom[custom_key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key."""
        parts = key.split(".")
        obj = self

        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                return default

        return obj

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding secrets)."""
        return {
            "server": {
                "host": self.server.host,
                "port": self.server.port,
                "reload": self.server.reload,
                "workers": self.server.workers,
                "timeout": self.server.timeout,
            },
            "security": {
                "allowed_origins": self.security.allowed_origins,
                "rate_limit": self.security.rate_limit,
                "enable_cors": self.security.enable_cors,
                # Secrets intentionally excluded
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file": self.logging.file,
                "max_size": self.logging.max_size,
                "backup_count": self.logging.backup_count,
            },
            "custom": self.custom,
            "discovered_plugins": list(self.plugins.keys()),
        }


class ConfigManager:
    """Singleton configuration manager for global access."""

    _instance: Optional[YaappConfig] = None

    @classmethod
    def get_config(cls) -> YaappConfig:
        """Get the global configuration instance."""
        if cls._instance is None:
            cls._instance = YaappConfig()
            cls._instance.load()
        return cls._instance

    @classmethod
    def set_config(cls, config: YaappConfig) -> None:
        """Set the global configuration instance."""
        cls._instance = config

    @classmethod
    def load_config(
        cls,
        config_file: Optional[Union[str, Path]] = None,
        secrets_file: Optional[Union[str, Path]] = None,
    ) -> YaappConfig:
        """Load and set global configuration."""
        cls._instance = YaappConfig.load(config_file, secrets_file)
        return cls._instance

