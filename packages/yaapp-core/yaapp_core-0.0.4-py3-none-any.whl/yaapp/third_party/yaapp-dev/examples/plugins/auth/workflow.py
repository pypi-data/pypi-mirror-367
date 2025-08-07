#!/usr/bin/env python3
"""
Auth Plugin Workflow Demo (Python Version)
==========================================
This script demonstrates the complete auth plugin workflow using direct Python calls.
Works without requiring Click to be installed.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path for imports
script_dir = Path(__file__).parent
repo_root = script_dir.parent.parent.parent
sys.path.insert(0, str(repo_root / "src"))

# Change to the auth example directory for configuration
os.chdir(script_dir)

from yaapp import yaapp

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color

def print_header(text):
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")

def print_step(step, description):
    print(f"\n{Colors.YELLOW}Step {step}: {description}{Colors.NC}")
    print("---")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.NC}")

def print_result(result, operation):
    if result.is_ok():
        data = result.unwrap()
        print(f"Result: {json.dumps(data, indent=2)}")
        print_success(f"{operation} successful")
        return data
    else:
        print_error(f"{operation} failed: {result.as_error}")
        return None

def main():
    print_header("🔐 yaapp Auth Plugin Workflow Demo (Python)")
    print("This script demonstrates the complete auth plugin workflow:")
    print("1. System information and admin token validation")
    print("2. User creation and management")
    print("3. User authentication (login/logout)")
    print("4. Token management")
    print("5. Role-based access control")
    print("")
    print("Initial admin token: admin_bootstrap_token_123")
    print(f"Script location: {script_dir}")
    print(f"Running from: {os.getcwd()}")
    print("")

    # Trigger plugin discovery
    yaapp._auto_discover_plugins()
    
    # Get auth plugin
    auth_result = yaapp.get_registry_item("auth")
    if auth_result.is_err():
        print_error(f"Failed to get auth plugin: {auth_result.as_error}")
        return False
    
    auth_plugin = auth_result.unwrap()
    print_success("Auth plugin loaded and ready")
    
    # Step 1: Get system information
    print_step("1", "Get Authentication System Information")
    result = auth_plugin.get_auth_info()
    auth_info = print_result(result, "Get auth info")
    if not auth_info:
        return False
    
    # Step 2: Validate admin token
    print_step("2", "Validate Initial Admin Token")
    admin_token = "admin_bootstrap_token_123"
    result = auth_plugin.validate_token(admin_token)
    token_info = print_result(result, "Validate admin token")
    if not token_info:
        return False
    
    # Step 3: Create regular user
    print_step("3", "Create a Regular User")
    result = auth_plugin.create_user(
        token=admin_token,
        username="alice",
        password="alice123",
        role="user"
    )
    alice_info = print_result(result, "Create user alice")
    if not alice_info:
        return False
    
    alice_user_id = alice_info['id']
    
    # Step 4: Create editor user
    print_step("4", "Create an Editor User")
    result = auth_plugin.create_user(
        token=admin_token,
        username="bob",
        password="bob456",
        role="editor"
    )
    bob_info = print_result(result, "Create user bob")
    if not bob_info:
        return False
    
    # Step 5: List all users
    print_step("5", "List All Users (Admin Operation)")
    result = auth_plugin.list_users(token=admin_token)
    users_list = print_result(result, "List users")
    if not users_list:
        return False
    
    # Step 6: User login
    print_step("6", "User Login (alice)")
    result = auth_plugin.login(username="alice", password="alice123")
    alice_login = print_result(result, "Alice login")
    if not alice_login:
        return False
    
    alice_token = alice_login['token']
    
    # Step 7: Get user profile
    print_step("7", "Get User Profile (alice)")
    result = auth_plugin.get_my_profile(token=alice_token)
    alice_profile = print_result(result, "Get Alice's profile")
    if not alice_profile:
        return False
    
    # Step 8: Try unauthorized operation
    print_step("8", "Try Unauthorized Operation (alice trying to list users)")
    result = auth_plugin.list_users(token=alice_token)
    if result.is_err():
        print_error(f"Unauthorized access correctly blocked: {result.as_error}")
        print_success("Access control working correctly")
    else:
        print_error("This should have failed (unauthorized access was allowed)")
        return False
    
    # Step 9: Create token for alice (admin operation)
    print_step("9", "Create Token for Alice (Admin Operation)")
    result = auth_plugin.create_token(
        token=admin_token,
        user_id=alice_user_id,
        expires="7d"
    )
    alice_new_token_info = print_result(result, "Create token for Alice")
    if not alice_new_token_info:
        return False
    
    alice_new_token = alice_new_token_info['token']
    
    # Step 10: Validate new token
    print_step("10", "Validate New Token")
    result = auth_plugin.validate_token(alice_new_token)
    new_token_info = print_result(result, "Validate Alice's new token")
    if not new_token_info:
        return False
    
    # Step 11: Change user role
    print_step("11", "Change User Role (Admin Operation)")
    result = auth_plugin.assign_role(
        token=admin_token,
        username="alice",
        role="editor"
    )
    role_change = print_result(result, "Assign editor role to Alice")
    if not role_change:
        return False
    
    # Step 12: Check permissions
    print_step("12", "Check User Permissions (Admin Operation)")
    result = auth_plugin.check_permission(
        token=admin_token,
        user_id=alice_user_id,
        resource="/api/data",
        action="read"
    )
    read_permission = print_result(result, "Check Alice's read permission")
    if not read_permission:
        return False
    
    print_step("12b", "Check Write Permission")
    result = auth_plugin.check_permission(
        token=admin_token,
        user_id=alice_user_id,
        resource="/api/data",
        action="write"
    )
    write_permission = print_result(result, "Check Alice's write permission")
    if not write_permission:
        return False
    
    # Step 13: User logout
    print_step("13", "User Logout")
    result = auth_plugin.logout(token=alice_token)
    logout_info = print_result(result, "Alice logout")
    if not logout_info:
        return False
    
    # Step 14: Try to use revoked token
    print_step("14", "Try to Use Revoked Token")
    result = auth_plugin.get_my_profile(token=alice_token)
    if result.is_err():
        print_error(f"Revoked token correctly rejected: {result.as_error}")
        print_success("Token revocation working correctly")
    else:
        print_error("This should have failed (revoked token was accepted)")
        return False
    
    # Step 15: Revoke token (admin operation)
    print_step("15", "Revoke Token (Admin Operation)")
    result = auth_plugin.revoke_token(
        token=admin_token,
        target_token=alice_new_token
    )
    revoke_info = print_result(result, "Revoke Alice's new token")
    if not revoke_info:
        return False
    
    # Step 16: Delete user
    print_step("16", "Delete User (Admin Operation)")
    result = auth_plugin.delete_user(
        token=admin_token,
        username="bob"
    )
    delete_info = print_result(result, "Delete user bob")
    if not delete_info:
        return False
    
    # Step 17: Final user list
    print_step("17", "Final User List")
    result = auth_plugin.list_users(token=admin_token)
    final_users = print_result(result, "Final user list")
    if not final_users:
        return False
    
    # Summary
    print_header("🎉 Workflow Complete!")
    print(f"{Colors.GREEN}✅ Successfully demonstrated all auth plugin features:{Colors.NC}")
    print("   • System information and token validation")
    print("   • User creation and management")
    print("   • User authentication (login/logout)")
    print("   • Token creation and management")
    print("   • Role assignment and permission checking")
    print("   • Access control and security boundaries")
    print("   • Token revocation and cleanup")
    print("")
    print(f"{Colors.BLUE}📋 Key Takeaways:{Colors.NC}")
    print("   • Use the initial admin token from yaapp.json for bootstrap operations")
    print("   • Admin operations require admin-level tokens")
    print("   • Users can only access their own profile and perform user-level operations")
    print("   • Tokens can be created, validated, and revoked")
    print("   • Role-based access control enforces security boundaries")
    print("   • All operations return structured JSON responses")
    print("")
    print(f"{Colors.YELLOW}🔧 Next Steps:{Colors.NC}")
    print("   • Integrate auth plugin with your application")
    print("   • Customize roles and permissions as needed")
    print("   • Set up proper token expiry policies")
    print("   • Consider using persistent storage (file/sqlite) for production")
    print("")
    print(f"{Colors.BLUE}📚 For more information, see:{Colors.NC}")
    print("   • examples/plugins/auth/README.md")
    print("   • examples/plugins/auth/USAGE.md")
    print("   • src/yaapp/plugins/auth/ (plugin source)")
    print("   • tests/examples/plugins/auth/ (test examples)")
    print("")
    print(f"{Colors.GREEN}🚀 Run from anywhere:{Colors.NC}")
    print("   • ./examples/plugins/auth/workflow.py (this script)")
    print("   • ./examples/plugins/auth/quick-start.sh")
    print("   • ./examples/plugins/auth/workflow.sh")
    print("   • ./examples/plugins/auth/auth-demo.sh (interactive launcher)")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Demo interrupted by user{Colors.NC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Demo failed with error: {e}{Colors.NC}")
        sys.exit(1)