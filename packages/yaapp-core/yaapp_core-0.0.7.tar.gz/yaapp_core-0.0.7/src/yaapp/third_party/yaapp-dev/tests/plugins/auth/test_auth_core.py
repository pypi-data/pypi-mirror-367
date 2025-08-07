"""
Tests for the auth plugin.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

import pytest
from yaapp import Yaapp, yaapp
from yaapp.result import Result


class TestAuthPlugin:
    """Test the auth plugin functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        # Clear the singleton registry first
        yaapp._registry.clear()
        
        # Configure storage plugin (required by auth) using singleton
        storage_config = {"backend": "memory"}
        yaapp.expose(self._create_storage_plugin(storage_config), name="storage")
        
        # Configure auth plugin
        auth_config = {
            "authentication": {
                "enabled": True,
                "methods": ["api_key"],
                "token_expiry": "24h",
                "initial_admin_token": "test_admin_token"
            },
            "authorization": {
                "enabled": True,
                "rbac_enabled": True,
                "default_role": "user",
                "admin_role": "admin"
            }
        }
        
        # Import and expose auth plugin using the decorator system
        from yaapp.plugins.auth.plugin import AuthPlugin
        auth_plugin = AuthPlugin(auth_config)
        
        # Set the yaapp instance on the auth plugin (required for proper initialization)
        auth_plugin.yaapp = yaapp
        
        yaapp.expose(auth_plugin, name="auth")
        
        # Store reference for easy access in tests
        self.auth_plugin = auth_plugin
    
    def _create_storage_plugin(self, config):
        """Create a simple storage plugin for testing."""
        class TestStorage:
            def __init__(self, config):
                self.data = {}
            
            def get(self, key, namespace=None):
                full_key = f"{namespace}:{key}" if namespace else key
                return self.data.get(full_key)
            
            def set(self, key, value, namespace=None, ttl_seconds=None):
                full_key = f"{namespace}:{key}" if namespace else key
                self.data[full_key] = value
                return True
            
            def delete(self, key, namespace=None):
                full_key = f"{namespace}:{key}" if namespace else key
                return self.data.pop(full_key, None) is not None
            
            def exists(self, key, namespace=None):
                full_key = f"{namespace}:{key}" if namespace else key
                return full_key in self.data
            
            def keys(self, pattern=None, namespace=None):
                prefix = f"{namespace}:" if namespace else ""
                matching_keys = []
                for key in self.data.keys():
                    if key.startswith(prefix):
                        clean_key = key[len(prefix):] if prefix else key
                        if pattern is None or pattern.replace("*", "") in clean_key:
                            matching_keys.append(clean_key)
                return matching_keys
        
        return TestStorage(config)
    
    def test_get_auth_info(self):
        """Test getting auth system information."""
        result = self.auth_plugin.get_auth_info()
        assert result.is_ok()
        
        info = result.unwrap()
        assert info["enabled"] is True
        assert "api_key" in info["methods"]
        assert info["rbac_enabled"] is True
        assert info["default_role"] == "user"
    
    def test_validate_admin_token(self):
        """Test validating the initial admin token."""
        result = self.auth_plugin.validate_token(token="test_admin_token")
        assert result.is_ok()
        
        token_info = result.unwrap()
        assert token_info["valid"] is True
        assert token_info["user_id"] == "admin"
        assert token_info["role"] == "admin"
    
    def test_create_user_as_admin(self):
        """Test creating a user with admin token."""
        result = self.auth_plugin.create_user(
            token="test_admin_token",
            username="testuser",
            password="testpass123",
            role="user"
        )
        assert result.is_ok()
        
        user_info = result.unwrap()
        assert user_info["username"] == "testuser"
        assert user_info["role"] == "user"
        assert "id" in user_info
        assert "created_at" in user_info
    
    def test_user_login(self):
        """Test user login with username/password."""
        # First create a user
        create_result = self.auth_plugin.create_user(
            token="test_admin_token",
            username="logintest",
            password="loginpass123"
        )
        assert create_result.is_ok()
        
        # Then login
        login_result = self.auth_plugin.login(
            username="logintest",
            password="loginpass123"
        )
        assert login_result.is_ok()
        
        login_info = login_result.unwrap()
        assert "token" in login_info
        assert login_info["username"] == "logintest"
        assert login_info["role"] == "user"  # default role
        assert "expires_at" in login_info
    
    def test_user_profile(self):
        """Test getting user profile with token."""
        # Create and login user
        self.auth_plugin.create_user(
            token="test_admin_token",
            username="profiletest",
            password="profilepass123"
        )
        
        login_result = self.auth_plugin.login(
            username="profiletest",
            password="profilepass123"
        )
        user_token = login_result.unwrap()["token"]
        
        # Get profile
        profile_result = self.auth_plugin.get_my_profile(token=user_token)
        assert profile_result.is_ok()
        
        profile = profile_result.unwrap()
        assert profile["username"] == "profiletest"
        assert profile["role"] == "user"
        assert profile["active"] is True
    
    def test_list_users_as_admin(self):
        """Test listing users with admin token."""
        # Create a test user first
        self.auth_plugin.create_user(
            token="test_admin_token",
            username="listtest",
            password="listpass123"
        )
        
        # List users
        result = self.auth_plugin.list_users(token="test_admin_token")
        assert result.is_ok()
        
        users = result.unwrap()
        assert len(users) >= 2  # admin + listtest
        
        usernames = [user["username"] for user in users]
        assert "admin" in usernames
        assert "listtest" in usernames
    
    def test_unauthorized_access(self):
        """Test that non-admin users cannot access admin endpoints."""
        # Create and login as regular user
        self.auth_plugin.create_user(
            token="test_admin_token",
            username="regularuser",
            password="regularpass123"
        )
        
        login_result = self.auth_plugin.login(
            username="regularuser",
            password="regularpass123"
        )
        user_token = login_result.unwrap()["token"]
        
        # Try to access admin endpoint
        result = self.auth_plugin.list_users(token=user_token)
        assert result.is_err()
        assert "Admin privileges required" in str(result.as_error)
    
    def test_invalid_token(self):
        """Test behavior with invalid token."""
        result = self.auth_plugin.validate_token(token="invalid_token")
        assert result.is_err()
        assert "Invalid token" in str(result.as_error)
    
    def test_logout(self):
        """Test user logout (token revocation)."""
        # Create and login user
        self.auth_plugin.create_user(
            token="test_admin_token",
            username="logouttest",
            password="logoutpass123"
        )
        
        login_result = self.auth_plugin.login(
            username="logouttest",
            password="logoutpass123"
        )
        user_token = login_result.unwrap()["token"]
        
        # Verify token works
        profile_result = self.auth_plugin.get_my_profile(token=user_token)
        assert profile_result.is_ok()
        
        # Logout
        logout_result = self.auth_plugin.logout(token=user_token)
        assert logout_result.is_ok()
        
        # Verify token no longer works
        profile_result2 = self.auth_plugin.get_my_profile(token=user_token)
        assert profile_result2.is_err()
        assert "Token has been revoked" in str(profile_result2.as_error)