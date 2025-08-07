#!/usr/bin/env python3
"""Simple test of the Universal API Plugin"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp.config import YaappConfig
from yaapp.plugins.api.plugin import Api

def main():
    """Run the API plugin tests."""
    print("🚀 Universal API Plugin - Simple Test")
    print("=====================================")
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    config_file = script_dir / "yaapp.yaml"
    
    # Change to the script directory so relative paths work
    original_cwd = os.getcwd()
    os.chdir(script_dir)
    
    try:
        # Load config directly
        config = YaappConfig.load(config_file=str(config_file))
        api_config = config.discovered_sections.get('api', {})
        
        if not api_config:
            print(f"❌ No API config found in {config_file}")
            return
    finally:
        # Always restore the original working directory
        os.chdir(original_cwd)
    
    print(f"📡 API Type: {api_config.get('type')}")
    print(f"🌐 Base URL: {api_config.get('base_url')}")
    print(f"📝 Description: {api_config.get('description')}")
    
    # Create and test the plugin (stay in script directory)
    os.chdir(script_dir)
    try:
        plugin = Api(api_config)
        plugin.expose_to_registry('api', None)
        
        methods = plugin._discovered_methods
        print(f"✅ Discovered {len(methods)} endpoints")
    finally:
        os.chdir(original_cwd)
    
    # Show some examples
    print(f"\n📋 Sample Endpoints:")
    for i, (method, info) in enumerate(methods.items()):
        if i >= 10:
            break
        path = info['path']
        http_method = info['method']
        summary = info.get('summary', '')[:50]
        print(f"   {method:<25} → {http_method:<6} {path}")
        if summary:
            print(f"   {'':<25}   {summary}")
    
    if len(methods) > 10:
        print(f"   ... and {len(methods) - 10} more endpoints")
    
    print(f"\n🎯 To use with yaapp:")
    print(f"   python app.py api --help")
    print(f"   python app.py api containers/json")

if __name__ == "__main__":
    main()