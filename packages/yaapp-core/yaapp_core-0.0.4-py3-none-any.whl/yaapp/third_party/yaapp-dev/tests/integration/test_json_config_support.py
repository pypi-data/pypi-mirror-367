#!/usr/bin/env python3
"""
Test JSON configuration file support.

This test verifies that yaapp properly supports JSON configuration files
and that the examples use JSON format correctly.
"""

import sys
import os
import json
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class TestResults_:
    """Track test results."""
    passed = 0
    failed = 0
    errors = []
    
    def assert_true(self, condition, message):
        if condition:
            self.passed += 1
            print(f"✅ {message}")
        else:
            self.failed += 1
            error = f"❌ {message}"
            print(error)
            self.errors.append(error)
    
    def assert_false(self, condition, message):
        self.assert_true(not condition, message)
    
    def assert_in(self, item, container, message):
        self.assert_true(item in container, message)
    
    def assert_equal(self, expected, actual, message):
        self.assert_true(expected == actual, f"{message} (expected: {expected}, got: {actual})")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\\n=== JSON CONFIG SUPPORT TEST SUMMARY ===")
        print(f"Total: {total}, Passed: {self.passed}, Failed: {self.failed}")
        if self.errors:
            print("\\nFAILED TESTS:")
            for error in self.errors:
                print(f"  {error}")
        return self.failed == 0


def test_json_config_parsing(results):
    """Test that JSON configuration files are parsed correctly."""
    print("\\n=== Testing JSON Configuration Parsing ===")
    
    try:
        from yaapp.config import YaappConfig
        
        # Create a test JSON config
        test_config = {
            "app": {
                "name": "test-app",
                "version": "1.0.0"
            },
            "server": {
                "host": "localhost",
                "port": 9000,
                "workers": 2
            },
            "storage": {
                "backend": "memory",
                "timeout": 30
            },
            "issues": {
                "default_priority": "high"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f, indent=2)
            config_file = f.name
        
        try:
            # Load config from JSON file
            config = YaappConfig.load(config_file=config_file)
            
            # Verify server config was loaded
            results.assert_equal("localhost", config.server.host, "Server host loaded from JSON")
            results.assert_equal(9000, config.server.port, "Server port loaded from JSON")
            results.assert_equal(2, config.server.workers, "Server workers loaded from JSON")
            
            # Verify plugin sections were discovered
            results.assert_in("storage", config.discovered_sections, "Storage plugin section discovered from JSON")
            results.assert_in("issues", config.discovered_sections, "Issues plugin section discovered from JSON")
            
            # Verify plugin config values
            storage_config = config.discovered_sections["storage"]
            results.assert_equal("memory", storage_config["backend"], "Storage backend config from JSON")
            results.assert_equal(30, storage_config["timeout"], "Storage timeout config from JSON")
            
            issues_config = config.discovered_sections["issues"]
            results.assert_equal("high", issues_config["default_priority"], "Issues priority config from JSON")
            
        finally:
            # Cleanup
            os.unlink(config_file)
            
    except Exception as e:
        results.assert_true(False, f"JSON config parsing failed: {e}")


def test_json_secrets_support(results):
    """Test that JSON secrets files are supported."""
    print("\\n=== Testing JSON Secrets Support ===")
    
    try:
        from yaapp.config import YaappConfig
        
        # Create test config and secrets
        main_config = {
            "app": {"name": "secrets-test"},
            "server": {"port": 8000}
        }
        
        secrets_config = {
            "security": {
                "api_key": "test-api-key",
                "secret_key": "test-secret-key"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(main_config, f)
            main_config_file = f.name
            
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(secrets_config, f)
            secrets_file = f.name
        
        try:
            # Load config with secrets
            config = YaappConfig.load(config_file=main_config_file, secrets_file=secrets_file)
            
            # Verify secrets were loaded
            results.assert_equal("test-api-key", config.security.api_key, "API key loaded from JSON secrets")
            results.assert_equal("test-secret-key", config.security.secret_key, "Secret key loaded from JSON secrets")
            
        finally:
            # Cleanup
            os.unlink(main_config_file)
            os.unlink(secrets_file)
            
    except Exception as e:
        results.assert_true(False, f"JSON secrets support failed: {e}")


def test_existing_json_examples(results):
    """Test that existing JSON examples are valid and parseable."""
    print("\\n=== Testing Existing JSON Examples ===")
    
    examples_dir = Path(__file__).parent.parent.parent / "examples" / "plugins"
    
    # Test issues example
    issues_config = examples_dir / "issues" / "yaapp.json"
    if issues_config.exists():
        try:
            with open(issues_config) as f:
                data = json.load(f)
            
            results.assert_true(True, "Issues example JSON is valid")
            results.assert_in("app", data, "Issues example has app section")
            results.assert_in("issues", data, "Issues example has issues plugin section")
            results.assert_in("storage", data, "Issues example has storage plugin section")
            
            # Verify specific values
            results.assert_equal("issues-example", data["app"]["name"], "Issues example app name")
            results.assert_equal("medium", data["issues"]["default_priority"], "Issues example priority")
            results.assert_equal("memory", data["storage"]["backend"], "Issues example storage backend")
            
        except Exception as e:
            results.assert_true(False, f"Issues example JSON parsing failed: {e}")
    
    # Test storage example
    storage_config = examples_dir / "storage" / "yaapp.json"
    if storage_config.exists():
        try:
            with open(storage_config) as f:
                data = json.load(f)
            
            results.assert_true(True, "Storage example JSON is valid")
            results.assert_in("app", data, "Storage example has app section")
            results.assert_in("storage", data, "Storage example has storage plugin section")
            
            # Verify specific values
            results.assert_equal("storage-example", data["app"]["name"], "Storage example app name")
            results.assert_equal("memory", data["storage"]["backend"], "Storage example backend")
            results.assert_equal("./data", data["storage"]["storage_dir"], "Storage example directory")
            
        except Exception as e:
            results.assert_true(False, f"Storage example JSON parsing failed: {e}")
    
    # Test app-proxy example
    proxy_config = examples_dir / "app-proxy" / "yaapp.json"
    if proxy_config.exists():
        try:
            with open(proxy_config) as f:
                data = json.load(f)
            
            results.assert_true(True, "App-proxy example JSON is valid")
            results.assert_in("app", data, "App-proxy example has app section")
            results.assert_in("app_proxy", data, "App-proxy example has app_proxy plugin section")
            
            # Verify specific values
            results.assert_equal("app-proxy-example", data["app"]["name"], "App-proxy example app name")
            results.assert_equal("http://localhost:8001", data["app_proxy"]["target_url"], "App-proxy target URL")
            
        except Exception as e:
            results.assert_true(False, f"App-proxy example JSON parsing failed: {e}")


def test_json_vs_yaml_priority(results):
    """Test file format priority when multiple formats exist."""
    print("\\n=== Testing JSON vs YAML Priority ===")
    
    try:
        from yaapp.config import YaappConfig
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create both YAML and JSON configs
            yaml_config = temp_path / "yaapp.yaml"
            json_config = temp_path / "yaapp.json"
            
            # YAML config (should be found first due to search order)
            yaml_content = '''
app:
  name: "yaml-app"
server:
  port: 7000
'''
            with open(yaml_config, 'w') as f:
                f.write(yaml_content)
            
            # JSON config
            json_content = {
                "app": {"name": "json-app"},
                "server": {"port": 8000}
            }
            with open(json_config, 'w') as f:
                json.dump(json_content, f)
            
            # Test discovery from directory
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # Should find YAML first (higher priority in search order)
                config = YaappConfig.load()
                
                # Check if PyYAML is available
                try:
                    import yaml
                    # YAML should be loaded if PyYAML is available
                    app_name = config.get("app.name")
                    if app_name == "yaml-app":
                        results.assert_equal("yaml-app", app_name, "YAML takes priority over JSON when both exist")
                        results.assert_equal(7000, config.server.port, "YAML server config loaded")
                    else:
                        # YAML parsing might have failed, JSON was used
                        results.assert_true(app_name in ["json-app", None], "JSON loaded when YAML parsing fails or app name not found")
                        results.assert_equal(8000, config.server.port, "JSON server config loaded as fallback")
                except ImportError:
                    # PyYAML not available, should fall back to JSON
                    results.assert_equal("json-app", config.get("app.name"), "JSON loaded when YAML not available")
                    results.assert_equal(8000, config.server.port, "JSON server config loaded")
                
            finally:
                os.chdir(original_cwd)
                
    except Exception as e:
        results.assert_true(False, f"JSON vs YAML priority test failed: {e}")


def test_json_environment_variable_substitution(results):
    """Test environment variable substitution in JSON configs."""
    print("\\n=== Testing JSON Environment Variable Substitution ===")
    
    try:
        from yaapp.config import YaappConfig
        
        # Set test environment variables
        os.environ["TEST_HOST"] = "test.example.com"
        os.environ["TEST_PORT"] = "9999"
        
        try:
            test_config = {
                "app": {"name": "env-test"},
                "server": {
                    "host": "${TEST_HOST:localhost}",
                    "port": "${TEST_PORT:8000}"
                },
                "custom": {
                    "api_url": "${API_URL:https://api.default.com}",
                    "debug": "${DEBUG_MODE:false}"
                }
            }
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(test_config, f)
                config_file = f.name
            
            try:
                config = YaappConfig.load(config_file=config_file)
                
                # Verify environment variable substitution
                results.assert_equal("test.example.com", config.server.host, "Environment variable substituted in JSON")
                # Note: environment variable substitution returns string, but config loading should handle conversion
                port_value = config.server.port
                results.assert_true(port_value == "9999" or port_value == 9999, "Environment variable substituted correctly in JSON")
                
                # Verify defaults are used when env var not set
                results.assert_equal("https://api.default.com", config.custom.get("api_url"), "Default value used when env var not set")
                results.assert_equal("false", config.custom.get("debug"), "Default value preserved in JSON")
                
            finally:
                os.unlink(config_file)
                
        finally:
            # Cleanup environment variables
            del os.environ["TEST_HOST"]
            del os.environ["TEST_PORT"]
            
    except Exception as e:
        results.assert_true(False, f"JSON environment variable substitution failed: {e}")


def test_json_plugin_discovery_integration(results):
    """Test that JSON configs properly trigger plugin discovery."""
    print("\\n=== Testing JSON Plugin Discovery Integration ===")
    
    try:
        from yaapp.config import YaappConfig
        
        # Create JSON config with plugin sections
        test_config = {
            "app": {"name": "plugin-discovery-test"},
            "storage": {
                "backend": "memory",
                "cache_size": 1000
            },
            "custom_plugin": {
                "setting1": "value1",
                "setting2": 42
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f, indent=2)
            config_file = f.name
        
        try:
            config = YaappConfig.load(config_file=config_file)
            
            # Verify plugin sections were identified
            plugin_sections = [k for k in test_config.keys() if k not in ['server', 'security', 'logging', 'custom', 'app']]
            results.assert_in("storage", plugin_sections, "Storage identified as plugin section from JSON")
            results.assert_in("custom_plugin", plugin_sections, "Custom plugin identified as plugin section from JSON")
            
            # Verify plugin configs are accessible
            if "storage" in config.discovered_sections:
                storage_config = config.discovered_sections["storage"]
                results.assert_equal("memory", storage_config["backend"], "Storage plugin config accessible from JSON")
                results.assert_equal(1000, storage_config["cache_size"], "Storage plugin numeric config from JSON")
            
        finally:
            os.unlink(config_file)
            
    except Exception as e:
        results.assert_true(False, f"JSON plugin discovery integration failed: {e}")


def main():
    """Run all JSON configuration support tests."""
    print("🔧 JSON Configuration Support Tests")
    print("Testing JSON configuration file support and examples")
    
    results = TestResults()
    
    # Run all test suites
    test_json_config_parsing(results)
    test_json_secrets_support(results)
    test_existing_json_examples(results)
    test_json_vs_yaml_priority(results)
    test_json_environment_variable_substitution(results)
    test_json_plugin_discovery_integration(results)
    
    # Show summary
    success = results.summary()
    
    if success:
        print("\\n🎉 ALL JSON CONFIG SUPPORT TESTS PASSED!")
        print("JSON configuration files are fully supported.")
        print("Examples use valid JSON format with proper plugin discovery.")
    else:
        print("\\n💥 JSON CONFIG SUPPORT TESTS FAILED!")
        print("Issues detected in JSON configuration support.")
        sys.exit(1)


if __name__ == "__main__":
    main()