"""
Unit tests for Git storage backend.
"""

# import pytest  # Removed for compatibility
import tempfile
import time
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from yaapp.plugins.storage.git.backend import GitStorage, GitStorageError


class TestGitStorage:
    """Test cases for GitStorage backend."""
    
    # @pytest.fixture - removed
    def temp_repo(self):
        """Create temporary repository for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test_repo"
            yield str(repo_path)
    
    # @pytest.fixture - removed
    def git_storage(self, temp_repo):
        """Create GitStorage instance for testing."""
        return GitStorage(
            repo_path=temp_repo,
            author_name="Test User",
            author_email="test@example.com",
            auto_gc=False  # Disable auto GC for tests
        )
    
    def test_initialization(self, temp_repo):
        """Test Git storage initialization."""
        storage = GitStorage(temp_repo)
        
        # Check repository was created
        repo_path = Path(temp_repo)
        assert repo_path.exists()
        assert (repo_path / ".git").exists()
        
        # Check README was created
        readme_path = repo_path / "README.md"
        assert readme_path.exists()
        assert "YAAPP Git Storage" in readme_path.read_text()
    
    def test_basic_operations(self, git_storage):
        """Test basic storage operations."""
        # Test set
        success = git_storage.set("test_key", {"data": "test_value"})
        assert success is True
        
        # Test get
        result = git_storage.get("test_key")
        assert result == {"data": "test_value"}
        
        # Test exists
        assert git_storage.exists("test_key") is True
        assert git_storage.exists("nonexistent_key") is False
        
        # Test delete
        deleted = git_storage.delete("test_key")
        assert deleted is True
        
        # Verify deletion
        assert git_storage.get("test_key") is None
        assert git_storage.exists("test_key") is False
    
    def test_data_types(self, git_storage):
        """Test storage of different data types."""
        test_cases = [
            ("string", "hello world"),
            ("integer", 42),
            ("float", 3.14159),
            ("boolean", True),
            ("list", [1, 2, 3, "four"]),
            ("dict", {"nested": {"data": "value"}}),
            ("none", None),
        ]
        
        for key, value in test_cases:
            git_storage.set(key, value)
            retrieved = git_storage.get(key)
            assert retrieved == value, f"Failed for {key}: {value}"
    
    def test_ttl_functionality(self, git_storage):
        """Test TTL (time-to-live) functionality."""
        # Set data with TTL
        git_storage.set("ttl_test", {"data": "expires"}, ttl_seconds=1)
        
        # Should exist immediately
        assert git_storage.exists("ttl_test") is True
        assert git_storage.get("ttl_test") == {"data": "expires"}
        
        # Wait for expiration
        time.sleep(2)
        
        # Should be expired
        assert git_storage.exists("ttl_test") is False
        assert git_storage.get("ttl_test") is None
    
    def test_keys_listing(self, git_storage):
        """Test key listing functionality."""
        # Add test data
        test_data = {
            "user:1": {"name": "Alice"},
            "user:2": {"name": "Bob"},
            "config:app": {"setting": "value"},
            "temp:session": {"id": "123"}
        }
        
        for key, value in test_data.items():
            git_storage.set(key, value)
        
        # Test listing all keys
        all_keys = git_storage.keys()
        assert len(all_keys) == 4
        for key in test_data.keys():
            assert key in all_keys
        
        # Test pattern matching
        user_keys = git_storage.keys("user:*")
        assert len(user_keys) == 2
        assert "user:1" in user_keys
        assert "user:2" in user_keys
        
        config_keys = git_storage.keys("config:*")
        assert len(config_keys) == 1
        assert "config:app" in config_keys
    
    def test_caching(self, git_storage):
        """Test caching functionality."""
        # Set data
        git_storage.set("cache_test", {"data": "cached"})
        
        # First read should populate cache
        result1 = git_storage.get("cache_test")
        assert result1 == {"data": "cached"}
        
        # Check cache was populated
        assert "cache_test" in git_storage._cache
        assert git_storage._cache["cache_test"] == {"data": "cached"}
        
        # Second read should use cache
        result2 = git_storage.get("cache_test")
        assert result2 == {"data": "cached"}
        
        # Delete should clear cache
        git_storage.delete("cache_test")
        assert "cache_test" not in git_storage._cache
    
    def test_clear_operation(self, git_storage):
        """Test clearing all data."""
        # Add test data
        for i in range(5):
            git_storage.set(f"clear_test_{i}", {"value": i})
        
        # Verify data exists
        assert len(git_storage.keys()) == 5
        
        # Clear all data
        cleared_count = git_storage.clear()
        assert cleared_count == 5
        
        # Verify all data is gone
        assert len(git_storage.keys()) == 0
        for i in range(5):
            assert git_storage.get(f"clear_test_{i}") is None
    
    def test_cleanup_expired(self, git_storage):
        """Test cleanup of expired items."""
        # Add regular data
        git_storage.set("regular", {"data": "permanent"})
        
        # Add data with TTL
        git_storage.set("expires1", {"data": "temp1"}, ttl_seconds=1)
        git_storage.set("expires2", {"data": "temp2"}, ttl_seconds=1)
        
        # Wait for expiration
        time.sleep(2)
        
        # Run cleanup
        cleaned_count = git_storage.cleanup_expired()
        assert cleaned_count == 2
        
        # Verify regular data still exists
        assert git_storage.exists("regular") is True
        
        # Verify expired data is gone
        assert git_storage.exists("expires1") is False
        assert git_storage.exists("expires2") is False
    
    def test_git_history(self, git_storage):
        """Test Git history functionality."""
        # Make several changes to the same key
        git_storage.set("history_test", {"version": 1})
        time.sleep(0.1)  # Small delay for different timestamps
        
        git_storage.set("history_test", {"version": 2})
        time.sleep(0.1)
        
        git_storage.set("history_test", {"version": 3})
        
        # Get history
        history = git_storage.get_history("history_test")
        
        # Should have at least 3 entries (one for each change)
        assert len(history) >= 3
        
        # Check history structure
        for entry in history:
            assert "commit_hash" in entry
            assert "author_name" in entry
            assert "author_email" in entry
            assert "date" in entry
            assert "message" in entry
            assert "Store: history_test" in entry["message"]
    
    def test_commit_data_retrieval(self, git_storage):
        """Test retrieving data from specific commits."""
        # Set initial data
        git_storage.set("commit_test", {"value": "initial"})
        
        # Get history to find commit
        history = git_storage.get_history("commit_test")
        if history:
            commit_hash = history[0]["commit_hash"]
            
            # Retrieve data from that commit
            commit_data = git_storage.get_commit_data(commit_hash, "commit_test")
            assert commit_data == {"value": "initial"}
    
    def test_repository_stats(self, git_storage):
        """Test repository statistics."""
        # Add some data
        for i in range(3):
            git_storage.set(f"stats_test_{i}", {"value": i})
        
        # Get stats
        stats = git_storage.get_repository_stats()
        
        # Check required fields
        assert "repository_path" in stats
        assert "total_commits" in stats
        assert "total_keys" in stats
        assert "cache_size" in stats
        assert "repository_size_bytes" in stats
        
        # Check values make sense
        assert stats["total_commits"] >= 4  # Initial + 3 data commits
        assert stats["total_keys"] == 3
        assert stats["repository_size_bytes"] > 0
    
    def test_backup_and_restore(self, git_storage, temp_repo):
        """Test backup and restore functionality."""
        # Add test data
        git_storage.set("backup_test", {"important": "data"})
        
        # Create backup
        backup_path = Path(temp_repo).parent / "backup_repo"
        backup_success = git_storage.create_backup(str(backup_path))
        assert backup_success is True
        assert backup_path.exists()
        
        # Verify backup contains data
        assert (backup_path / "objects").exists()
        assert (backup_path / "refs").exists()
        
        # Add more data to original
        git_storage.set("after_backup", {"new": "data"})
        assert git_storage.exists("after_backup") is True
        
        # Restore from backup
        restore_success = git_storage.restore_from_backup(str(backup_path))
        assert restore_success is True
        
        # Verify original data exists
        assert git_storage.get("backup_test") == {"important": "data"}
        
        # Verify new data is gone (restored to backup state)
        assert git_storage.exists("after_backup") is False
    
    def test_error_handling(self, git_storage):
        """Test error handling scenarios."""
        # Test getting non-existent key
        result = git_storage.get("nonexistent")
        assert result is None
        
        # Test deleting non-existent key
        deleted = git_storage.delete("nonexistent")
        assert deleted is False
        
        # Test invalid JSON data handling
        with patch.object(git_storage, '_load_data_from_file') as mock_load:
            mock_load.return_value = None
            result = git_storage.get("test_key")
            assert result is None
    
    def test_concurrent_access(self, git_storage):
        """Test concurrent access patterns."""
        import threading
        import queue
        
        results = queue.Queue()
        errors = queue.Queue()
        
        def worker(worker_id):
            try:
                for i in range(10):
                    key = f"worker_{worker_id}_item_{i}"
                    data = {"worker": worker_id, "item": i}
                    
                    # Set data
                    success = git_storage.set(key, data)
                    if not success:
                        errors.put(f"Worker {worker_id}: Failed to set {key}")
                        continue
                    
                    # Get data
                    retrieved = git_storage.get(key)
                    if retrieved != data:
                        errors.put(f"Worker {worker_id}: Data mismatch for {key}")
                        continue
                    
                    results.put(f"Worker {worker_id}: Success for {key}")
                    
            except Exception as e:
                errors.put(f"Worker {worker_id}: Exception {e}")
        
        # Start multiple workers
        threads = []
        for worker_id in range(3):
            thread = threading.Thread(target=worker, args=(worker_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = results.qsize()
        error_count = errors.qsize()
        
        assert success_count == 30  # 3 workers * 10 items each
        assert error_count == 0
        
        # Verify all data exists
        all_keys = git_storage.keys()
        worker_keys = [key for key in all_keys if key.startswith("worker_")]
        assert len(worker_keys) == 30
    
    @patch('subprocess.run')
    def test_git_command_failure(self, mock_run, temp_repo):
        """Test handling of Git command failures."""
        # Mock Git command failure
        mock_run.side_effect = Exception("Git command failed")
        
        with pytest.raises(GitStorageError):
            GitStorage(temp_repo)
    
    def test_file_system_errors(self, git_storage):
        """Test handling of file system errors."""
        # Test with invalid file path
        with patch.object(git_storage, '_get_data_file_path') as mock_path:
            mock_path.return_value = Path("/invalid/path/file.json")
            
            # Should handle file system errors gracefully
            success = git_storage.set("test", {"data": "value"})
            assert success is False
    
    def test_large_data_handling(self, git_storage):
        """Test handling of large data objects."""
        # Create large data object
        large_data = {
            "large_list": list(range(10000)),
            "large_string": "x" * 100000,
            "nested_data": {
                f"key_{i}": f"value_{i}" * 100
                for i in range(1000)
            }
        }
        
        # Should handle large data
        success = git_storage.set("large_data", large_data)
        assert success is True
        
        # Should retrieve correctly
        retrieved = git_storage.get("large_data")
        assert retrieved == large_data
    
    def test_special_characters_in_keys(self, git_storage):
        """Test handling of special characters in keys."""
        special_keys = [
            "key with spaces",
            "key-with-dashes",
            "key_with_underscores",
            "key.with.dots",
            "key/with/slashes",
            "key:with:colons",
            "key@with@symbols",
        ]
        
        for key in special_keys:
            data = {"key": key, "data": "test"}
            
            # Should handle special characters
            success = git_storage.set(key, data)
            assert success is True
            
            # Should retrieve correctly
            retrieved = git_storage.get(key)
            assert retrieved == data
            
            # Should list correctly
            keys = git_storage.keys()
            assert key in keys