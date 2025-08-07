"""
Comprehensive tests for the auth plugin example.

This test suite verifies that the auth plugin works correctly with the yaapp framework,
including auto-discovery, configuration, and all authentication/authorization features.
"""

import os
import sys
import tempfile
import json
from pathlib import Path
from typing import Dict, Any

# import pytest  # Not needed for direct execution

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from yaapp import yaapp, Yaapp
from yaapp.result import Result


class TestAuthPluginExample:
    """Test the auth plugin example functionality."""
    
    def setup_method(self):
        """Set up test environment for each test."""
        # Create a temporary directory for the test
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        
        # Create test configuration
        self.config = {
            "app": {
                "name": "auth-test-example",
                "description": "Test auth plugin functionality"
            },
            "auth": {
                "authentication": {
                    "enabled": True,
                    "methods": ["api_key", "jwt"],
                    "token_expiry": "24h",
                    "initial_admin_token": "test_admin_token_123"
                },
                "authorization": {
                    "enabled": True,
                    "rbac_enabled": True,
                    "default_role": "user",
                    "admin_role": "admin"
                },
                "storage": {
                    "path": "/data/auth"
                }
            },
            "storage": {
                "backend": "memory"
            },
            "server": {
                "port": 8000,
                "host": "localhost"
            }
        }
        
        # Write config file
        config_file = Path(self.test_dir) / "yaapp.json"
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        # Change to test directory
        os.chdir(self.test_dir)
        
        # Use the singleton yaapp instance and trigger discovery
        self.app = yaapp
        self.app._auto_discover_plugins()
        
        # Manually instantiate plugins with proper configuration
        self._setup_plugins()
    
    def teardown_method(self):
        """Clean up after each test."""
        os.chdir(self.original_cwd)
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _setup_plugins(self):
        """Set up plugins with proper instantiation."""
        # Load configuration
        config = self.app._load_config()
        
        # Get plugin classes from registry
        auth_result = self.app.get_registry_item("auth")
        storage_result = self.app.get_registry_item("storage")
        
        if auth_result.is_err() or storage_result.is_err():
            print(f"Plugins not properly discovered: auth={auth_result.is_err()}, storage={storage_result.is_err()}")
            return
        
        # Get plugin instances (they should already be instantiated by our fix)
        storage_obj = storage_result.unwrap()
        auth_obj = auth_result.unwrap()
        
        # Check if they're already instances or still classes
        if isinstance(storage_obj, type):
            # Still a class, need to instantiate
            storage_config = config.discovered_sections.get('storage', {})
            self.storage_plugin = storage_obj(storage_config)
            self.storage_plugin.yaapp = self.app
            self.app._registry['storage'] = (self.storage_plugin, self.app._registry['storage'][1])
        else:
            # Already an instance
            self.storage_plugin = storage_obj
        
        if isinstance(auth_obj, type):
            # Still a class, need to instantiate
            auth_config = config.discovered_sections.get('auth', {})
            self.auth_plugin = auth_obj(auth_config)
            self.auth_plugin.yaapp = self.app
            self.app._registry['auth'] = (self.auth_plugin, self.app._registry['auth'][1])
        else:
            # Already an instance
            self.auth_plugin = auth_obj
        
        # Clear storage to ensure clean state
        cleared_count = self.storage_plugin.clear()
        print(f"Cleared {cleared_count} items from storage")
        
        # Re-initialize auth plugin to recreate admin user
        self.auth_plugin._initialized = False
        self.auth_plugin._initialization_attempted = False
    
    def test_plugin_discovery(self):
        """Test that plugins are properly discovered."""
        registry = self.app.get_registry_items()
        assert 'auth' in registry, "Auth plugin should be discovered"
        assert 'storage' in registry, "Storage plugin should be discovered"
        
        # Verify plugins are properly instantiated
        assert hasattr(self.auth_plugin, 'get_auth_info'), "Auth plugin should have get_auth_info method"
        assert hasattr(self.storage_plugin, 'get'), "Storage plugin should have get method"
    
    def test_auth_info_endpoint(self):
        """Test the public auth info endpoint."""
        result = self.auth_plugin.get_auth_info()
        
        assert result.is_ok(), f"get_auth_info should succeed: {result.as_error if result.is_err() else ''}"
        
        info = result.unwrap()
        assert info['enabled'] is True
        assert 'api_key' in info['methods']
        assert 'jwt' in info['methods']
        assert info['rbac_enabled'] is True
        assert info['default_role'] == 'user'
        assert info['token_expiry_hours'] == 24
    
    def test_admin_token_validation(self):
        """Test validation of the initial admin token."""
        result = self.auth_plugin.validate_token("test_admin_token_123")
        
        assert result.is_ok(), f"Admin token validation should succeed: {result.as_error if result.is_err() else ''}"
        
        token_info = result.unwrap()
        assert token_info['valid'] is True
        assert token_info['user_id'] == 'admin'
        assert token_info['role'] == 'admin'
        assert 'expires_at' in token_info
    
    def test_invalid_token_validation(self):
        """Test validation of invalid tokens."""
        result = self.auth_plugin.validate_token("invalid_token_123")
        
        assert result.is_err(), "Invalid token validation should fail"
        assert "Invalid token" in str(result.as_error)
    
    def test_user_creation_workflow(self):
        """Test the complete user creation workflow."""
        # Test creating a user with admin token
        result = self.auth_plugin.create_user(
            token="test_admin_token_123",
            username="testuser",
            password="testpass123",
            role="user"
        )
        
        assert result.is_ok(), f"User creation should succeed: {result.as_error if result.is_err() else ''}"
        
        user_info = result.unwrap()
        assert user_info['username'] == 'testuser'
        assert user_info['role'] == 'user'
        assert 'id' in user_info
        assert 'created_at' in user_info
        
        return user_info
    
    def test_user_login_workflow(self):
        """Test the complete user login workflow."""
        # First create a user
        user_info = self.test_user_creation_workflow()
        
        # Test login with correct credentials
        result = self.auth_plugin.login(
            username="testuser",
            password="testpass123"
        )
        
        assert result.is_ok(), f"User login should succeed: {result.as_error if result.is_err() else ''}"
        
        login_info = result.unwrap()
        assert 'token' in login_info
        assert login_info['username'] == 'testuser'
        assert login_info['role'] == 'user'
        assert login_info['user_id'] == user_info['id']
        assert 'expires_at' in login_info
        
        return login_info
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        # First create a user
        self.test_user_creation_workflow()
        
        # Test login with wrong password
        result = self.auth_plugin.login(
            username="testuser",
            password="wrongpassword"
        )
        
        assert result.is_err(), "Login with wrong password should fail"
        assert "Invalid username or password" in str(result.as_error)
    
    def test_user_profile_access(self):
        """Test user profile access with valid token."""
        # Create user and login
        login_info = self.test_user_login_workflow()
        user_token = login_info['token']
        
        # Get user profile
        result = self.auth_plugin.get_my_profile(token=user_token)
        
        assert result.is_ok(), f"Profile access should succeed: {result.as_error if result.is_err() else ''}"
        
        profile = result.unwrap()
        assert profile['username'] == 'testuser'
        assert profile['role'] == 'user'
        assert profile['active'] is True
        assert 'id' in profile
        assert 'created_at' in profile
    
    def test_user_profile_invalid_token(self):
        """Test user profile access with invalid token."""
        result = self.auth_plugin.get_my_profile(token="invalid_token")
        
        assert result.is_err(), "Profile access with invalid token should fail"
        assert "Invalid token" in str(result.as_error)
    
    def test_admin_list_users(self):
        """Test admin functionality to list users."""
        # Create a test user first
        self.test_user_creation_workflow()
        
        # List users with admin token
        result = self.auth_plugin.list_users(token="test_admin_token_123")
        
        assert result.is_ok(), f"List users should succeed: {result.as_error if result.is_err() else ''}"
        
        users = result.unwrap()
        assert len(users) >= 2, "Should have at least admin and test user"
        
        # Check admin user exists
        admin_users = [u for u in users if u['username'] == 'admin']
        assert len(admin_users) == 1, "Should have exactly one admin user"
        assert admin_users[0]['role'] == 'admin'
        
        # Check test user exists
        test_users = [u for u in users if u['username'] == 'testuser']
        assert len(test_users) == 1, "Should have exactly one test user"
        assert test_users[0]['role'] == 'user'
    
    def test_admin_list_users_unauthorized(self):
        """Test that non-admin users cannot list users."""
        # Create user and login
        login_info = self.test_user_login_workflow()
        user_token = login_info['token']
        
        # Try to list users with user token
        result = self.auth_plugin.list_users(token=user_token)
        
        assert result.is_err(), "Non-admin user should not be able to list users"
        assert "Admin privileges required" in str(result.as_error)
    
    def test_admin_create_token_for_user(self):
        """Test admin creating tokens for users."""
        # Create a test user
        user_info = self.test_user_creation_workflow()
        user_id = user_info['id']
        
        # Create token for user with admin privileges
        result = self.auth_plugin.create_token(
            token="test_admin_token_123",
            user_id=user_id,
            expires="7d"
        )
        
        assert result.is_ok(), f"Token creation should succeed: {result.as_error if result.is_err() else ''}"
        
        token_info = result.unwrap()
        assert 'token' in token_info
        assert token_info['user_id'] == user_id
        assert token_info['username'] == 'testuser'
        assert token_info['role'] == 'user'
        assert 'expires_at' in token_info
        
        # Verify the created token works
        validation_result = self.auth_plugin.validate_token(token_info['token'])
        assert validation_result.is_ok(), "Created token should be valid"
    
    def test_admin_create_token_unauthorized(self):
        """Test that non-admin users cannot create tokens."""
        # Create user and login
        login_info = self.test_user_login_workflow()
        user_token = login_info['token']
        user_id = login_info['user_id']
        
        # Try to create token with user privileges
        result = self.auth_plugin.create_token(
            token=user_token,
            user_id=user_id,
            expires="1h"
        )
        
        assert result.is_err(), "Non-admin user should not be able to create tokens"
        assert "Admin privileges required" in str(result.as_error)
    
    def test_user_logout(self):
        """Test user logout functionality."""
        # Create user and login
        login_info = self.test_user_login_workflow()
        user_token = login_info['token']
        
        # Verify token works before logout
        profile_result = self.auth_plugin.get_my_profile(token=user_token)
        assert profile_result.is_ok(), "Token should work before logout"
        
        # Logout
        logout_result = self.auth_plugin.logout(token=user_token)
        assert logout_result.is_ok(), f"Logout should succeed: {logout_result.as_error if logout_result.is_err() else ''}"
        
        logout_info = logout_result.unwrap()
        assert "Successfully logged out" in logout_info['message']
        
        # Verify token no longer works after logout
        profile_result2 = self.auth_plugin.get_my_profile(token=user_token)
        assert profile_result2.is_err(), "Token should not work after logout"
        assert "Token has been revoked" in str(profile_result2.as_error)
    
    def test_admin_revoke_token(self):
        """Test admin revoking user tokens."""
        # Create user and login
        login_info = self.test_user_login_workflow()
        user_token = login_info['token']
        
        # Verify token works before revocation
        profile_result = self.auth_plugin.get_my_profile(token=user_token)
        assert profile_result.is_ok(), "Token should work before revocation"
        
        # Admin revokes the token
        revoke_result = self.auth_plugin.revoke_token(
            token="test_admin_token_123",
            target_token=user_token
        )
        assert revoke_result.is_ok(), f"Token revocation should succeed: {revoke_result.as_error if revoke_result.is_err() else ''}"
        
        # Verify token no longer works after revocation
        profile_result2 = self.auth_plugin.get_my_profile(token=user_token)
        assert profile_result2.is_err(), "Token should not work after revocation"
        assert "Token has been revoked" in str(profile_result2.as_error)
    
    def test_admin_assign_role(self):
        """Test admin assigning roles to users."""
        # Create a test user
        self.test_user_creation_workflow()
        
        # Assign editor role to user
        result = self.auth_plugin.assign_role(
            token="test_admin_token_123",
            username="testuser",
            role="editor"
        )
        
        assert result.is_ok(), f"Role assignment should succeed: {result.as_error if result.is_err() else ''}"
        
        role_info = result.unwrap()
        assert "Role 'editor' assigned to user 'testuser'" in role_info['message']
        
        # Verify role change by logging in
        login_result = self.auth_plugin.login(
            username="testuser",
            password="testpass123"
        )
        assert login_result.is_ok(), "Login should still work after role change"
        
        login_info = login_result.unwrap()
        assert login_info['role'] == 'editor', "User should have new role"
    
    def test_admin_check_permission(self):
        """Test admin checking user permissions."""
        # Create a test user
        user_info = self.test_user_creation_workflow()
        user_id = user_info['id']
        
        # Check permission for user
        result = self.auth_plugin.check_permission(
            token="test_admin_token_123",
            user_id=user_id,
            resource="/api/data",
            action="read"
        )
        
        assert result.is_ok(), f"Permission check should succeed: {result.as_error if result.is_err() else ''}"
        
        perm_info = result.unwrap()
        assert perm_info['user_id'] == user_id
        assert perm_info['username'] == 'testuser'
        assert perm_info['role'] == 'user'
        assert perm_info['resource'] == '/api/data'
        assert perm_info['action'] == 'read'
        assert perm_info['allowed'] is True  # Users can read by default
    
    def test_admin_check_permission_write_denied(self):
        """Test that regular users cannot write by default."""
        # Create a test user
        user_info = self.test_user_creation_workflow()
        user_id = user_info['id']
        
        # Check write permission for user
        result = self.auth_plugin.check_permission(
            token="test_admin_token_123",
            user_id=user_id,
            resource="/api/data",
            action="write"
        )
        
        assert result.is_ok(), f"Permission check should succeed: {result.as_error if result.is_err() else ''}"
        
        perm_info = result.unwrap()
        assert perm_info['allowed'] is False  # Users cannot write by default
    
    def test_admin_permissions_all_allowed(self):
        """Test that admin users have all permissions."""
        # Check admin permissions
        result = self.auth_plugin.check_permission(
            token="test_admin_token_123",
            user_id="admin",
            resource="/api/admin",
            action="delete"
        )
        
        assert result.is_ok(), f"Permission check should succeed: {result.as_error if result.is_err() else ''}"
        
        perm_info = result.unwrap()
        assert perm_info['user_id'] == 'admin'
        assert perm_info['role'] == 'admin'
        assert perm_info['allowed'] is True  # Admin has all permissions
    
    def test_user_creation_duplicate_username(self):
        """Test that duplicate usernames are rejected."""
        # Create first user
        self.test_user_creation_workflow()
        
        # Try to create user with same username
        result = self.auth_plugin.create_user(
            token="test_admin_token_123",
            username="testuser",  # Same username
            password="differentpass",
            role="user"
        )
        
        assert result.is_err(), "Duplicate username should be rejected"
        assert "User 'testuser' already exists" in str(result.as_error)
    
    def test_user_deletion(self):
        """Test admin deleting users."""
        # Create a test user
        self.test_user_creation_workflow()
        
        # Verify user exists
        users_result = self.auth_plugin.list_users(token="test_admin_token_123")
        assert users_result.is_ok()
        users_before = users_result.unwrap()
        test_users_before = [u for u in users_before if u['username'] == 'testuser']
        assert len(test_users_before) == 1, "Test user should exist before deletion"
        
        # Delete user
        delete_result = self.auth_plugin.delete_user(
            token="test_admin_token_123",
            username="testuser"
        )
        
        assert delete_result.is_ok(), f"User deletion should succeed: {delete_result.as_error if delete_result.is_err() else ''}"
        
        delete_info = delete_result.unwrap()
        assert "User 'testuser' deleted successfully" in delete_info['message']
        
        # Verify user no longer exists
        users_result2 = self.auth_plugin.list_users(token="test_admin_token_123")
        assert users_result2.is_ok()
        users_after = users_result2.unwrap()
        test_users_after = [u for u in users_after if u['username'] == 'testuser']
        assert len(test_users_after) == 0, "Test user should not exist after deletion"
    
    def test_cannot_delete_admin_user(self):
        """Test that admin user cannot be deleted."""
        result = self.auth_plugin.delete_user(
            token="test_admin_token_123",
            username="admin"
        )
        
        assert result.is_err(), "Admin user deletion should be rejected"
        assert "Cannot delete admin user" in str(result.as_error)
    
    def test_password_change(self):
        """Test user changing their own password."""
        # Create user and login
        login_info = self.test_user_login_workflow()
        user_token = login_info['token']
        
        # Change password
        change_result = self.auth_plugin.change_password(
            token=user_token,
            current_password="testpass123",
            new_password="newpass456"
        )
        
        assert change_result.is_ok(), f"Password change should succeed: {change_result.as_error if change_result.is_err() else ''}"
        
        change_info = change_result.unwrap()
        assert "Password changed successfully" in change_info['message']
        
        # Verify old password no longer works
        old_login_result = self.auth_plugin.login(
            username="testuser",
            password="testpass123"
        )
        assert old_login_result.is_err(), "Old password should not work"
        
        # Verify new password works
        new_login_result = self.auth_plugin.login(
            username="testuser",
            password="newpass456"
        )
        assert new_login_result.is_ok(), "New password should work"
    
    def test_password_change_wrong_current_password(self):
        """Test password change with wrong current password."""
        # Create user and login
        login_info = self.test_user_login_workflow()
        user_token = login_info['token']
        
        # Try to change password with wrong current password
        change_result = self.auth_plugin.change_password(
            token=user_token,
            current_password="wrongpass",
            new_password="newpass456"
        )
        
        assert change_result.is_err(), "Password change with wrong current password should fail"
        assert "Current password is incorrect" in str(change_result.as_error)


def test_auth_example_integration():
    """Integration test that runs the full auth example workflow."""
    # This test can be run independently to verify the auth plugin works
    test_instance = TestAuthPluginExample()
    test_instance.setup_method()
    
    try:
        # Run a subset of key tests
        test_instance.test_plugin_discovery()
        test_instance.test_auth_info_endpoint()
        test_instance.test_admin_token_validation()
        test_instance.test_user_creation_workflow()
        test_instance.test_user_login_workflow()
        test_instance.test_user_profile_access()
        test_instance.test_admin_list_users()
        test_instance.test_user_logout()
        
        print("✅ All auth plugin integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Auth plugin integration test failed: {e}")
        return False
        
    finally:
        test_instance.teardown_method()


if __name__ == "__main__":
    # Run integration test when script is executed directly
    success = test_auth_example_integration()
    sys.exit(0 if success else 1)