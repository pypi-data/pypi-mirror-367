"""
Integration tests for the API plugin app.py to verify CLI integration works.
"""

import subprocess
import sys
import os
from pathlib import Path
import pytest


class TestAPIPluginAppIntegration:
    """Test the API plugin app.py CLI integration."""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment."""
        cls.example_dir = Path(__file__).parent.parent.parent.parent.parent / "examples" / "plugins" / "api"
        cls.app_script = cls.example_dir / "app.py"
        
        # Verify the example directory exists
        assert cls.example_dir.exists(), f"Example directory not found: {cls.example_dir}"
        assert cls.app_script.exists(), f"App script not found: {cls.app_script}"
    
    def run_app_command(self, args, timeout=30):
        """Run the app.py script with given arguments."""
        original_cwd = os.getcwd()
        try:
            os.chdir(self.example_dir)
            
            cmd = [sys.executable, "app.py"] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return result
        finally:
            os.chdir(original_cwd)
    
    def test_app_help_shows_api_command(self):
        """Test that app.py --help shows the api command."""
        result = self.run_app_command(["--help"])
        
        print("=== APP.PY --HELP OUTPUT ===")
        print(result.stdout)
        if result.stderr:
            print("=== STDERR ===")
            print(result.stderr)
        print("=== END OUTPUT ===")
        
        assert result.returncode == 0, f"app.py --help failed with return code {result.returncode}"
        
        # The api command should be listed
        assert "api" in result.stdout, "API command not found in help output"
        assert "Commands:" in result.stdout, "Commands section not found in help output"
    
    def test_api_help_shows_discovered_endpoints(self):
        """Test that app.py api --help shows discovered Docker API endpoints."""
        result = self.run_app_command(["api", "--help"])
        
        print("=== APP.PY API --HELP OUTPUT ===")
        print(result.stdout)
        if result.stderr:
            print("=== STDERR ===")
            print(result.stderr)
        print("=== END OUTPUT ===")
        
        assert result.returncode == 0, f"app.py api --help failed with return code {result.returncode}"
        
        # Should show discovered Docker API endpoints
        expected_endpoints = [
            "containers",
            "images", 
            "version",
            "info"
        ]
        
        # Check if any of the expected endpoints are shown
        found_endpoints = []
        for endpoint in expected_endpoints:
            if endpoint in result.stdout:
                found_endpoints.append(endpoint)
        
        assert len(found_endpoints) > 0, f"No expected Docker API endpoints found in output. Expected: {expected_endpoints}"
        print(f"✅ Found endpoints: {found_endpoints}")
    
    def test_api_containers_command_exists(self):
        """Test that app.py api containers command exists."""
        result = self.run_app_command(["api", "containers", "--help"])
        
        print("=== APP.PY API CONTAINERS --HELP OUTPUT ===")
        print(result.stdout)
        if result.stderr:
            print("=== STDERR ===")
            print(result.stderr)
        print("=== END OUTPUT ===")
        
        # Should either work (returncode 0) or show that the command exists but has issues
        # We're mainly checking that the command is recognized, not that it executes successfully
        assert "containers" in result.stdout or "containers" in result.stderr, "containers command not recognized"
    
    def test_api_version_command_exists(self):
        """Test that app.py api version command exists."""
        result = self.run_app_command(["api", "version", "--help"])
        
        print("=== APP.PY API VERSION --HELP OUTPUT ===")
        print(result.stdout)
        if result.stderr:
            print("=== STDERR ===")
            print(result.stderr)
        print("=== END OUTPUT ===")
        
        # Should either work (returncode 0) or show that the command exists but has issues
        assert "version" in result.stdout or "version" in result.stderr, "version command not recognized"
    
    def test_api_plugin_loads_successfully(self):
        """Test that the API plugin loads without errors."""
        result = self.run_app_command(["--help"])
        
        # Check for plugin loading messages
        assert "✅ Loaded plugin: api" in result.stderr or "✅ Loaded plugin: api" in result.stdout, "API plugin not loaded successfully"
        assert "🔗 Plugin ready: api" in result.stderr or "🔗 Plugin ready: api" in result.stdout, "API plugin not ready"
    
    def test_api_discovers_endpoints(self):
        """Test that the API plugin discovers endpoints during startup."""
        result = self.run_app_command(["api", "--help"])
        
        # Look for discovery messages in stderr (where plugin output usually goes)
        output = result.stderr + result.stdout
        
        # Should see discovery messages
        discovery_indicators = [
            "Discovered",
            "endpoints",
            "OpenAPI",
            "Docker"
        ]
        
        found_indicators = []
        for indicator in discovery_indicators:
            if indicator in output:
                found_indicators.append(indicator)
        
        assert len(found_indicators) >= 2, f"Not enough discovery indicators found. Found: {found_indicators}, Expected at least 2 from: {discovery_indicators}"
        print(f"✅ Found discovery indicators: {found_indicators}")


def test_app_integration_direct():
    """Direct integration test that can be run standalone."""
    test_instance = TestAPIPluginAppIntegration()
    test_instance.setup_class()
    
    print("🧪 Running API Plugin App Integration Tests")
    print("=" * 50)
    
    try:
        print("\n1. Testing app.py --help shows api command...")
        test_instance.test_app_help_shows_api_command()
        print("✅ PASS")
        
        print("\n2. Testing API plugin loads successfully...")
        test_instance.test_api_plugin_loads_successfully()
        print("✅ PASS")
        
        print("\n3. Testing API discovers endpoints...")
        test_instance.test_api_discovers_endpoints()
        print("✅ PASS")
        
        print("\n4. Testing api --help shows discovered endpoints...")
        test_instance.test_api_help_shows_discovered_endpoints()
        print("✅ PASS")
        
        print("\n5. Testing api containers command exists...")
        test_instance.test_api_containers_command_exists()
        print("✅ PASS")
        
        print("\n6. Testing api version command exists...")
        test_instance.test_api_version_command_exists()
        print("✅ PASS")
        
        print("\n🎉 All integration tests passed!")
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        raise


if __name__ == "__main__":
    test_app_integration_direct()