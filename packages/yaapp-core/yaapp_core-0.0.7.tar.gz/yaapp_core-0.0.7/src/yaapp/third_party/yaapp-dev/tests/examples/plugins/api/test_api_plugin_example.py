#!/usr/bin/env python3
"""
Comprehensive tests for the Universal API Plugin example.

This test suite verifies that the API plugin example works correctly
by running the simple-test.py script and validating its output.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "src"))

class TestAPIPluginExample:
    """Test suite for the Universal API Plugin example."""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment."""
        cls.example_dir = Path(__file__).parent.parent.parent.parent.parent / "examples" / "plugins" / "api"
        cls.simple_test_script = cls.example_dir / "simple-test.py"
        
        # Verify the example directory exists
        assert cls.example_dir.exists(), f"Example directory not found: {cls.example_dir}"
        assert cls.simple_test_script.exists(), f"Simple test script not found: {cls.simple_test_script}"
    
    def run_simple_test(self, config_file="yaapp.yaml", timeout=60):
        """Run the simple-test.py script and return the result."""
        # Change to the example directory
        original_cwd = os.getcwd()
        try:
            os.chdir(self.example_dir)
            
            # Ensure the config file exists
            config_path = self.example_dir / config_file
            assert config_path.exists(), f"Config file not found: {config_path}"
            
            # Run the simple test script
            result = subprocess.run(
                [sys.executable, "simple-test.py"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return result
        finally:
            os.chdir(original_cwd)
    
    def test_docker_api_discovery(self):
        """Test Docker API discovery with default config."""
        result = self.run_simple_test("yaapp.yaml")
        
        # Check that the script ran successfully
        assert result.returncode == 0, f"Script failed with error: {result.stderr}"
        
        output = result.stdout
        
        # Verify key output elements
        assert "🚀 Universal API Plugin - Simple Test" in output
        assert "📡 API Type: openapi" in output
        assert "🌐 Base URL: http://localhost/v1.42" in output
        assert "Docker Engine API" in output
        assert "✅ Discovered" in output and "endpoints" in output
        
        # Verify specific Docker endpoints are discovered
        assert "containers/json" in output
        assert "containers/create" in output
        assert "containers/inspect" in output
        assert "images/" in output or "containers/" in output
        
        # Verify endpoint details
        assert "GET" in output and "POST" in output  # HTTP methods
        assert "/containers/" in output  # API paths
        
        print("✅ Docker API discovery test passed")
    
    def test_httpbin_api_discovery(self):
        """Test HTTPBin API discovery."""
        # Copy HTTPBin config
        original_cwd = os.getcwd()
        try:
            os.chdir(self.example_dir)
            shutil.copy("yaapp-httpbin.yaml", "yaapp.yaml")
            
            result = self.run_simple_test("yaapp.yaml")
            
            # Check that the script ran successfully
            assert result.returncode == 0, f"Script failed with error: {result.stderr}"
            
            output = result.stdout
            
            # Verify HTTPBin-specific output
            assert "📡 API Type: openapi" in output
            assert "🌐 Base URL: https://httpbin.org" in output
            assert "HTTPBin API" in output
            assert "✅ Discovered" in output and "endpoints" in output
            
            # Verify specific HTTPBin endpoints
            assert "get" in output or "post" in output or "basic-auth" in output
            
            print("✅ HTTPBin API discovery test passed")
            
        finally:
            os.chdir(original_cwd)
            # Restore original config
            try:
                os.chdir(self.example_dir)
                if os.path.exists("yaapp-docker.yaml"):
                    shutil.copy("yaapp-docker.yaml", "yaapp.yaml")
                else:
                    # Restore Docker config
                    with open("yaapp.yaml", "w") as f:
                        f.write("""app:
  name: api-example

api:
  type: openapi
  spec_url: https://raw.githubusercontent.com/docker/engine/master/api/swagger.yaml
  base_url: http://localhost/v1.42
  transport: unix_socket
  socket_path: /var/run/docker.sock
  description: Docker Engine API - Full Docker API with 88+ endpoints for container management

server:
  port: 8000
  host: localhost""")
            except:
                pass
            os.chdir(original_cwd)
    
    def test_petstore_api_discovery(self):
        """Test Swagger Petstore API discovery."""
        # Copy Petstore config
        original_cwd = os.getcwd()
        try:
            os.chdir(self.example_dir)
            shutil.copy("yaapp-petstore.yaml", "yaapp.yaml")
            
            result = self.run_simple_test("yaapp.yaml")
            
            # Check that the script ran successfully
            assert result.returncode == 0, f"Script failed with error: {result.stderr}"
            
            output = result.stdout
            
            # Verify Petstore-specific output
            assert "📡 API Type: openapi" in output
            assert "🌐 Base URL: https://petstore3.swagger.io" in output
            assert "Swagger Petstore" in output
            assert "✅ Discovered" in output and "endpoints" in output
            
            # Verify specific Petstore endpoints
            assert "pet" in output or "store" in output or "user" in output
            
            print("✅ Petstore API discovery test passed")
            
        finally:
            os.chdir(original_cwd)
            # Restore original config
            try:
                os.chdir(self.example_dir)
                # Restore Docker config
                with open("yaapp.yaml", "w") as f:
                    f.write("""app:
  name: api-example

api:
  type: openapi
  spec_url: https://raw.githubusercontent.com/docker/engine/master/api/swagger.yaml
  base_url: http://localhost/v1.42
  transport: unix_socket
  socket_path: /var/run/docker.sock
  description: Docker Engine API - Full Docker API with 88+ endpoints for container management

server:
  port: 8000
  host: localhost""")
            except:
                pass
            os.chdir(original_cwd)
    
    def test_config_files_exist(self):
        """Test that all required config files exist."""
        config_files = [
            "yaapp.yaml",
            "yaapp-httpbin.yaml", 
            "yaapp-petstore.yaml"
        ]
        
        for config_file in config_files:
            config_path = self.example_dir / config_file
            assert config_path.exists(), f"Config file missing: {config_file}"
            
            # Verify it's valid YAML
            import yaml
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Verify required structure
            assert 'api' in config_data, f"Missing 'api' section in {config_file}"
            assert 'type' in config_data['api'], f"Missing 'type' in api section of {config_file}"
            assert config_data['api']['type'] == 'openapi', f"Invalid type in {config_file}"
            assert 'spec_url' in config_data['api'], f"Missing 'spec_url' in {config_file}"
            assert 'base_url' in config_data['api'], f"Missing 'base_url' in {config_file}"
        
        print("✅ Config files validation test passed")
    
    def test_plugin_import(self):
        """Test that the API plugin can be imported correctly."""
        try:
            from yaapp.plugins.api.plugin import Api
            
            # Test basic instantiation
            plugin = Api({})
            assert hasattr(plugin, 'expose_to_registry')
            assert hasattr(plugin, 'execute_call')
            
            print("✅ Plugin import test passed")
            
        except ImportError as e:
            pytest.fail(f"Failed to import API plugin: {e}")
    
    def test_endpoint_count_validation(self):
        """Test that reasonable numbers of endpoints are discovered."""
        result = self.run_simple_test("yaapp.yaml")
        
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        
        output = result.stdout
        
        # Extract endpoint count
        import re
        match = re.search(r'✅ Discovered (\d+) endpoints', output)
        assert match, "Could not find endpoint count in output"
        
        endpoint_count = int(match.group(1))
        
        # Docker API should have a reasonable number of endpoints (50-150)
        assert 50 <= endpoint_count <= 150, f"Unexpected endpoint count: {endpoint_count}"
        
        print(f"✅ Endpoint count validation passed: {endpoint_count} endpoints")


def test_run_simple_test_directly():
    """Direct test that runs simple-test.py and validates output."""
    example_dir = Path(__file__).parent.parent.parent.parent.parent / "examples" / "plugins" / "api"
    
    # Change to example directory and run the test
    original_cwd = os.getcwd()
    try:
        os.chdir(example_dir)
        
        result = subprocess.run(
            [sys.executable, "simple-test.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print("=== SIMPLE-TEST.PY OUTPUT ===")
        print(result.stdout)
        if result.stderr:
            print("=== STDERR ===")
            print(result.stderr)
        print("=== END OUTPUT ===")
        
        # Basic validation
        assert result.returncode == 0, f"simple-test.py failed with return code {result.returncode}"
        assert "✅ Discovered" in result.stdout, "No endpoints discovered"
        assert "endpoints" in result.stdout, "Missing endpoint information"
        
        print("✅ Direct simple-test.py execution passed")
        
    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    # Run the direct test when script is executed
    test_run_simple_test_directly()
    
    # Run the full test suite
    test_instance = TestAPIPluginExample()
    test_instance.setup_class()
    
    print("\n🧪 Running Universal API Plugin Tests")
    print("=" * 50)
    
    try:
        test_instance.test_config_files_exist()
        test_instance.test_plugin_import()
        test_instance.test_docker_api_discovery()
        test_instance.test_endpoint_count_validation()
        test_instance.test_httpbin_api_discovery()
        test_instance.test_petstore_api_discovery()
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise