#!/usr/bin/env python3
"""
Basic Git Storage Usage Example

Demonstrates fundamental operations with the Git storage backend:
- Storing and retrieving data
- TTL (time-to-live) functionality
- Basic querying and listing
- Cache behavior
"""

import tempfile
import time
from pathlib import Path

# Import YAAPP storage
from yaapp.plugins.storage import create_git_storage_manager


def main():
    print("🚀 Git Storage - Basic Usage Example")
    print("=" * 50)
    
    # Create temporary directory for this demo
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "git_storage_demo"
        
        print(f"📁 Creating Git storage at: {repo_path}")
        
        # Create Git storage manager
        storage = create_git_storage_manager(
            repo_path=str(repo_path),
            author_name="Demo User",
            author_email="demo@example.com"
        )
        
        print("✅ Git storage initialized")
        print()
        
        # Basic storage operations
        print("📝 Basic Storage Operations")
        print("-" * 30)
        
        # Store some data
        print("Storing user data...")
        success = storage.set("user:123", {
            "name": "Alice Smith",
            "email": "alice@example.com",
            "role": "admin",
            "created_at": "2024-01-15T10:30:00Z"
        })
        print(f"✅ Store result: {success}")
        
        # Store configuration
        print("Storing configuration...")
        config_data = {
            "app_name": "My YAAPP Application",
            "version": "1.0.0",
            "debug": False,
            "features": ["auth", "storage", "api"]
        }
        storage.set("config:app", config_data)
        
        # Store with TTL (expires in 5 seconds)
        print("Storing temporary data with TTL...")
        storage.set("temp:session", {"session_id": "abc123", "expires": True}, ttl_seconds=5)
        
        print()
        
        # Retrieve data
        print("📖 Retrieving Data")
        print("-" * 20)
        
        user_data = storage.get("user:123")
        print(f"User data: {user_data}")
        
        config = storage.get("config:app")
        print(f"Config: {config}")
        
        temp_data = storage.get("temp:session")
        print(f"Temp data: {temp_data}")
        
        print()
        
        # List all keys
        print("📋 Listing Keys")
        print("-" * 15)
        
        all_keys = storage.keys()
        print(f"All keys: {all_keys}")
        
        # Pattern matching
        user_keys = storage.keys("user:*")
        print(f"User keys: {user_keys}")
        
        config_keys = storage.keys("config:*")
        print(f"Config keys: {config_keys}")
        
        print()
        
        # Check existence
        print("🔍 Checking Existence")
        print("-" * 20)
        
        print(f"user:123 exists: {storage.exists('user:123')}")
        print(f"user:999 exists: {storage.exists('user:999')}")
        print(f"temp:session exists: {storage.exists('temp:session')}")
        
        print()
        
        # Wait for TTL expiration
        print("⏰ Testing TTL Expiration")
        print("-" * 25)
        
        print("Waiting 6 seconds for TTL expiration...")
        time.sleep(6)
        
        temp_data_after = storage.get("temp:session")
        print(f"Temp data after expiration: {temp_data_after}")
        print(f"temp:session exists after expiration: {storage.exists('temp:session')}")
        
        print()
        
        # Update existing data
        print("✏️  Updating Data")
        print("-" * 16)
        
        # Get current user data
        current_user = storage.get("user:123")
        print(f"Current user: {current_user}")
        
        # Update user data
        updated_user = current_user.copy()
        updated_user["role"] = "super_admin"
        updated_user["last_login"] = "2024-01-16T14:20:00Z"
        
        storage.set("user:123", updated_user)
        
        # Verify update
        final_user = storage.get("user:123")
        print(f"Updated user: {final_user}")
        
        print()
        
        # Delete data
        print("🗑️  Deleting Data")
        print("-" * 16)
        
        print("Deleting config...")
        deleted = storage.delete("config:app")
        print(f"Delete result: {deleted}")
        
        # Verify deletion
        config_after_delete = storage.get("config:app")
        print(f"Config after deletion: {config_after_delete}")
        
        print()
        
        # Final key listing
        print("📋 Final Key Listing")
        print("-" * 20)
        
        final_keys = storage.keys()
        print(f"Remaining keys: {final_keys}")
        
        print()
        
        # Storage statistics
        print("📊 Storage Statistics")
        print("-" * 20)
        
        # Access the Git backend directly for stats
        git_backend = storage.get_backend("default")
        if hasattr(git_backend, 'get_repository_stats'):
            stats = git_backend.get_repository_stats()
            print(f"Repository path: {stats.get('repository_path')}")
            print(f"Total commits: {stats.get('total_commits')}")
            print(f"Total keys: {stats.get('total_keys')}")
            print(f"Cache size: {stats.get('cache_size')}")
            print(f"Repository size: {stats.get('repository_size_bytes')} bytes")
            
            latest_commit = stats.get('latest_commit', {})
            if latest_commit:
                print(f"Latest commit: {latest_commit.get('hash', '')[:8]} - {latest_commit.get('message', '')}")
        
        print()
        print("🎉 Basic usage demonstration complete!")
        print("=" * 50)


if __name__ == "__main__":
    main()