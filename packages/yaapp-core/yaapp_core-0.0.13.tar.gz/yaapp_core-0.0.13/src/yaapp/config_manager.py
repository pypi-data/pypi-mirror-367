"""
ConfigManager - Handles declarative config loading and plugin activation.

Receives yaapp_engine and uses it to activate plugins based on config sections.
No boilerplate - everything is declarative.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Config manager that receives yaapp_engine and activates plugins declaratively."""
    
    def load(self, yaapp_engine, config_file: Optional[str] = None) -> None:
        """Load config and activate plugins - main entry point.
        
        Args:
            yaapp_engine: YaappEngine instance to activate plugins on
            config_file: Optional config file path
        """
        config_data = self._load(config_file)
        self._activate_plugins_from_config(yaapp_engine, config_data)
    
    def _load(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file - internal method for testing.
        
        Args:
            config_file: Optional config file path
            
        Returns:
            Configuration data dictionary
        """
        # Auto-detect config file if not provided
        if config_file is None:
            config_file = self._find_config_file()
        
        if not config_file or not Path(config_file).exists():
            return {}
        
        try:
            return self._parse_config_file(config_file)
        except (FileNotFoundError, PermissionError, OSError, ValueError, TypeError) as e:
            # Protect against file I/O and parsing issues (foreign libraries)
            print(f"Warning: Failed to load config from {config_file}: {e}")
            return {}
    
    def _find_config_file(self) -> Optional[str]:
        """Find config file in current directory."""
        # Look for yaapp.yaml, yaapp.yml, yaapp.json in current directory
        for filename in ['yaapp.yaml', 'yaapp.yml', 'yaapp.json']:
            if Path(filename).exists():
                return filename
        return None
    
    def _parse_config_file(self, config_file: str) -> Dict[str, Any]:
        """Parse config file (YAML or JSON)."""
        config_path = Path(config_file)
        
        with open(config_path, 'r') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                try:
                    import yaml
                    return yaml.safe_load(f) or {}
                except ImportError:
                    print("Warning: YAML config found but PyYAML not installed")
                    return {}
            else:
                import json
                return json.load(f) or {}
    
    def _activate_plugins_from_config(self, yaapp_engine, config_data: Dict[str, Any]) -> None:
        """Activate plugins based on config sections.
        
        Args:
            yaapp_engine: YaappEngine instance
            config_data: Configuration data
        """
        if not config_data:
            return
        
        # Reserved sections that are not plugins
        reserved_sections = {
            'app', 'server', 'security', 'logging', 'custom', 
            'execution_mode', 'auto_sampling', 'execution_engine', 
            'cli', 'environment'
        }
        
        # Find plugin sections (any section not in reserved list)
        plugin_sections = {
            key: value for key, value in config_data.items()
            if key not in reserved_sections and isinstance(value, dict)
        }
        
        if not plugin_sections:
            return
        
        
        
        # Activate each plugin
        for plugin_name, plugin_config in plugin_sections.items():
            yaapp_engine.activate_plugin(plugin_name, plugin_config)