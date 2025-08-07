"""
CORRECT Plugin Discovery - Filesystem-based, NO imports during discovery.

DISCOVERY: Just scan filesystem for plugin.py files
LOADING: Import only when plugin is actually used
"""

import importlib
from pathlib import Path
from typing import Dict, Any, List, Optional


def discover_plugins_metadata(plugin_path: str = None) -> Dict[str, Dict[str, Any]]:
    """Discover plugin metadata WITHOUT importing - just filesystem scan.
    
    Args:
        plugin_path: Colon-separated paths to search for plugins
    
    Returns:
        Dict of plugin_name -> plugin_metadata (NO plugin classes!)
    """
    plugins_metadata = {}
    
    # Get search paths
    if plugin_path:
        search_paths = plugin_path.split(':')
    else:
        # Default paths
        search_paths = [
            str(Path(__file__).parent / "plugins"),
            "third_party/yaapp-plugins/src/yaapp/plugins"
        ]
    
    for search_path in search_paths:
        found_metadata = _scan_plugins_in_path(search_path)
        plugins_metadata.update(found_metadata)
    
    return plugins_metadata


def _scan_plugins_in_path(search_path: str) -> Dict[str, Dict[str, Any]]:
    """Scan for plugins in a path - NO IMPORTS, just filesystem check.
    
    Args:
        search_path: Path to search for plugins
    
    Returns:
        Dict of plugin_name -> plugin_metadata
    """
    plugins_metadata = {}
    
    try:
        plugins_dir = Path(search_path)
        if not plugins_dir.exists():
            return plugins_metadata
        
        for plugin_path in plugins_dir.iterdir():
            if plugin_path.is_dir() and not plugin_path.name.startswith('_'):
                plugin_name = plugin_path.name
                plugin_file = plugin_path / "plugin.py"
                
                # JUST CHECK IF plugin.py EXISTS - NO IMPORT!
                if plugin_file.exists():
                    plugins_metadata[plugin_name] = {
                        "name": plugin_name,
                        "path": str(plugin_path),
                        "plugin_file": str(plugin_file),
                        "search_path": search_path,
                        "discovered": True,
                        "loaded": False  # Not loaded yet!
                    }
                    
                
    except (OSError, FileNotFoundError) as e:
        print(f"Warning: Failed to scan plugin path {search_path}: {e}")
    
    return plugins_metadata


def load_plugin_class(plugin_metadata: Dict[str, Any]) -> Optional[Any]:
    """Load a specific plugin class by importing - ONLY when needed.
    
    Args:
        plugin_metadata: Plugin metadata from discovery
    
    Returns:
        Plugin class or None if failed
    """
    plugin_name = plugin_metadata["name"]
    search_path = plugin_metadata["search_path"]
    
    try:
        # Set up sys.path appropriately
        import sys
        
        # Determine if this is a built-in plugin directory
        is_builtin_path = ("src/yaapp/plugins" in search_path and "yaapp-plugins" not in search_path)
        
        if is_builtin_path:
            # For built-in plugins, ensure src is in path
            src_dir = search_path.replace("/yaapp/plugins", "")
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
            module_path = f"yaapp.plugins.{plugin_name}.plugin"
        else:
            # For external plugins, add the plugin directory to path
            plugins_dir = Path(search_path)
            if str(plugins_dir) not in sys.path:
                sys.path.insert(0, str(plugins_dir))
            module_path = f"{plugin_name}.plugin"
        
        # NOW we import - only for this specific plugin
        module = importlib.import_module(module_path)
        
        # Look for plugin class (convention: capitalized plugin name)
        class_name = plugin_name.capitalize()
        if hasattr(module, class_name):
            plugin_class = getattr(module, class_name)
            
            return plugin_class
        else:
            print(f"Warning: Plugin {plugin_name} has no {class_name} class")
            return None
            
    except ImportError as e:
        print(f"Warning: Failed to import plugin {plugin_name}: {e}")
        return None


def discover_runners() -> Dict[str, Any]:
    """Discover runner modules from runners/ directory.
    
    Each runner should be a <subdirectory>/runner.py module with run() and help() functions.
    
    Returns:
        Dict of runner_name -> runner_module
    """
    runners = {}
    
    try:
        # Scan runners directory
        runners_dir = Path(__file__).parent / "runners"
        if runners_dir.exists():
            for runner_path in runners_dir.iterdir():
                if runner_path.is_dir() and not runner_path.name.startswith('_'):
                    runner_name = runner_path.name
                    
                    # Try to import runner module
                    try:
                        module_path = f"yaapp.runners.{runner_name}.runner"
                        module = importlib.import_module(module_path)
                        
                        # Check if module has required run() function
                        if hasattr(module, 'run') and callable(getattr(module, 'run')):
                            runners[runner_name] = module
                    except ImportError:
                        continue
    except (ImportError, AttributeError, OSError, FileNotFoundError):
        # Protect against import and file system issues (foreign operations)
        pass
    
    return runners


def get_available_plugins_metadata(plugin_path: str = None) -> List[Dict[str, Any]]:
    """Get list of available plugin metadata - NO IMPORTS."""
    plugins_metadata = discover_plugins_metadata(plugin_path)
    return list(plugins_metadata.values())


def get_available_plugin_names(plugin_path: str = None) -> List[str]:
    """Get list of available plugin names - NO IMPORTS."""
    plugins_metadata = discover_plugins_metadata(plugin_path)
    return list(plugins_metadata.keys())


def get_available_runners() -> List[str]:
    """Get list of available runner names."""
    return list(discover_runners().keys())


# LEGACY COMPATIBILITY - but now uses correct approach
def discover_plugins(plugin_path: str = None) -> Dict[str, Any]:
    """Legacy function - now returns metadata instead of classes.
    
    IMPORTANT: This now returns metadata, not plugin classes!
    Use load_plugin_class() to actually load a plugin.
    """
    return discover_plugins_metadata(plugin_path)