#!/usr/bin/env python3
"""
Example demonstrating the enhanced YAAPP configuration system.

This example shows how to use:
- Environment variable substitution in config files
- Environment variable overrides
- Secrets file management
- Configuration priority ordering
"""

import os
import tempfile
import json
from pathlib import Path
import sys

# Add src to path for example
sys.path.insert(0, "../src")

from yaapp import Yaapp
from yaapp.config import YaappConfig


def create_example_config_files():
    """Create example configuration files."""
    print("Creating example configuration files...")
    
    # Create main config file with environment variable substitution
    config_data = {
        "server": {
            "host": "${YAAPP_HOST:localhost}",
            "port": 8080,
            "workers": 2,
            "timeout": 30
        },
        "security": {
            "allowed_origins": ["https://example.com"],
            "rate_limit": 1000,
            "enable_cors": True
        },
        "logging": {
            "level": "${LOG_LEVEL:INFO}",
            "file": "${LOG_FILE:/tmp/yaapp.log}",
            "max_size": 10000000
        },
        "custom": {
            "app_name": "YAAPP Configuration Demo",
            "version": "1.0.0",
            "environment": "${ENVIRONMENT:development}"
        }
    }
    
    with open("yaapp.yaml", "w") as f:
        import yaml
        yaml.dump(config_data, f, default_flow_style=False)
    
    # Create secrets file (would normally be encrypted/secured)
    secrets_data = {
        "security": {
            "api_key": "${SECRET_API_KEY:demo-api-key}",
            "secret_key": "${SECRET_KEY:demo-secret-key}"
        }
    }
    
    with open("yaapp.secrets.yaml", "w") as f:
        yaml.dump(secrets_data, f, default_flow_style=False)
    
    print("✅ Configuration files created:")
    print("   - yaapp.yaml (main configuration)")
    print("   - yaapp.secrets.yaml (secrets)")


def demonstrate_config_loading():
    """Demonstrate different ways to load configuration."""
    print("\n🔧 Configuration Loading Demonstration")
    
    # 1. Load configuration with defaults
    print("\n1. Loading with defaults:")
    config = YaappConfig.load()
    print(f"   Server host: {config.server.host}")
    print(f"   Server port: {config.server.port}")
    print(f"   Log level: {config.logging.level}")
    
    # 2. Set environment variables to override defaults
    print("\n2. Setting environment variables:")
    os.environ["YAAPP_HOST"] = "production.example.com"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["ENVIRONMENT"] = "production"
    os.environ["SECRET_API_KEY"] = "prod-api-key-123"
    
    # Reload configuration (environment variables take precedence)
    config = YaappConfig.load()
    print(f"   Server host: {config.server.host} (from env substitution)")
    print(f"   Server port: {config.server.port} (from file)")
    print(f"   Log level: {config.logging.level} (from env substitution)")
    print(f"   Environment: {config.custom.get('environment')} (from env substitution)")
    print(f"   API key: {config.security.api_key} (from secrets with env substitution)")
    
    # 3. Direct environment overrides (highest priority)
    print("\n3. Setting direct environment overrides:")
    os.environ["YAAPP_SERVER_PORT"] = "9000"
    os.environ["YAAPP_LOG_LEVEL"] = "ERROR"
    
    config = YaappConfig.load()
    print(f"   Server host: {config.server.host} (from env substitution in file)")
    print(f"   Server port: {config.server.port} (from direct env override)")
    print(f"   Log level: {config.logging.level} (from direct env override)")


def demonstrate_yaapp_integration():
    """Demonstrate integration with YApp."""
    print("\n🚀 YApp Integration Demonstration")
    
    # Set app configuration
    os.environ["YAAPP_CUSTOM_APP_NAME"] = "My Enhanced YAAPP Application"
    
    # Create Yaapp instance (automatically loads enhanced config)
    app = Yaapp()
    
    # Add some example functions
    @app.expose
    def get_config_info():
        """Get information about the current configuration."""
        config = app.core._load_config()
        return {
            "app_name": config.custom.get("app_name", "YAAPP"),
            "server_host": config.server.host,
            "server_port": config.server.port,
            "log_level": config.logging.level,
            "environment": config.custom.get("environment", "unknown")
        }
    
    @app.expose
    def show_all_config():
        """Show all configuration (excluding secrets)."""
        config = app.core._load_config()
        return config.to_dict()
    
    print(f"✅ Yaapp created with enhanced configuration")
    print(f"   App name: {app.core._get_app_name()}")
    
    # Test the exposed functions
    config_info = get_config_info()
    print(f"   Configuration info: {config_info}")
    
    return app


def cleanup_example_files():
    """Clean up example files."""
    files_to_remove = ["yaapp.yaml", "yaapp.secrets.yaml"]
    for file in files_to_remove:
        if Path(file).exists():
            Path(file).unlink()
    
    # Clean up environment variables
    env_vars_to_clean = [
        "YAAPP_HOST", "LOG_LEVEL", "ENVIRONMENT", "SECRET_API_KEY", "SECRET_KEY",
        "YAAPP_SERVER_PORT", "YAAPP_LOG_LEVEL", "YAAPP_CUSTOM_APP_NAME"
    ]
    for var in env_vars_to_clean:
        if var in os.environ:
            del os.environ[var]


if __name__ == "__main__":
    print("🎯 YAAPP Enhanced Configuration System Demo")
    print("=" * 50)
    
    try:
        # Check if PyYAML is available
        import yaml
        HAS_YAML = True
    except ImportError:
        print("⚠️  PyYAML not available - using JSON examples instead")
        HAS_YAML = False
    
    if HAS_YAML:
        create_example_config_files()
        demonstrate_config_loading()
        app = demonstrate_yaapp_integration()
        
        print("\n💡 Key Features Demonstrated:")
        print("   ✅ Environment variable substitution (${VAR:default})")
        print("   ✅ Environment overrides (YAAPP_SECTION_KEY)")
        print("   ✅ Secrets file auto-merging")
        print("   ✅ Configuration priority: ENV > Config File > Secrets > Defaults")
        print("   ✅ Type-safe configuration with validation")
        print("   ✅ Integration with YApp core")
        
        print(f"\n🔧 You can now run the application:")
        print(f"   python -c \"from configuration_example import demonstrate_yaapp_integration; app = demonstrate_yaapp_integration(); app.run_cli()\"")
        
        cleanup_example_files()
    else:
        print("Please install PyYAML to run this example: pip install pyyaml")
        print("The configuration system also supports JSON files if YAML is not available.")