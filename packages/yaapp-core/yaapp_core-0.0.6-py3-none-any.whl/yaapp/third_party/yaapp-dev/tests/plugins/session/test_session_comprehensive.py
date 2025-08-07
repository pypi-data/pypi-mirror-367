#!/usr/bin/env python3
"""
Comprehensive tests for Session plugin functionality.
"""

import pytest
import sys
import time
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from yaapp.plugins.session.plugin import (
    SessionHandler, 
    MemorySessionStorage, 
    FileSessionStorage,
    create_memory_session_handler,
    create_file_session_handler
)


class TestMemorySessionStorage:
    """Test MemorySessionStorage functionality."""
    
    @pytest.fixture
    def storage(self):
        """Create a MemorySessionStorage instance for testing."""
        return MemorySessionStorage()
    
    def test_memory_storage_initialization(self, storage):
        """Test MemorySessionStorage initialization."""
        assert storage._sessions == {}
        assert storage._expiry == {}
    
    def test_set_and_get_session(self, storage):
        """Test setting and getting session data."""
        session_data = {"user_id": 123, "username": "testuser"}
        
        # Set session
        result = storage.set("session123", session_data)
        assert result is True
        
        # Get session
        retrieved = storage.get("session123")
        assert retrieved == session_data
        assert retrieved is not session_data  # Should be a copy
    
    def test_set_with_ttl(self, storage):
        """Test setting session with TTL."""
        session_data = {"user_id": 123}
        
        # Set with 1 second TTL
        storage.set("session123", session_data, ttl_seconds=1)
        
        # Should be available immediately
        assert storage.get("session123") == session_data
        
        # Wait for expiry
        time.sleep(1.1)
        
        # Should be expired
        assert storage.get("session123") is None
    
    def test_delete_session(self, storage):
        """Test deleting session."""
        session_data = {"user_id": 123}
        storage.set("session123", session_data)
        
        # Verify it exists
        assert storage.get("session123") == session_data
        
        # Delete it
        result = storage.delete("session123")
        assert result is True
        
        # Verify it's gone
        assert storage.get("session123") is None
        
        # Delete non-existent session
        result = storage.delete("nonexistent")
        assert result is False
    
    def test_cleanup_expired(self, storage):
        """Test cleanup of expired sessions."""
        # Set sessions with different TTLs
        storage.set("session1", {"data": "1"}, ttl_seconds=1)
        storage.set("session2", {"data": "2"}, ttl_seconds=2)
        storage.set("session3", {"data": "3"})  # No TTL
        
        # Wait for first session to expire
        time.sleep(1.1)
        
        # Cleanup expired
        removed_count = storage.cleanup_expired()
        assert removed_count == 1
        
        # Verify correct sessions remain
        assert storage.get("session1") is None
        assert storage.get("session2") is not None
        assert storage.get("session3") is not None


class TestFileSessionStorage:
    """Test FileSessionStorage functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for file storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def storage(self, temp_dir):
        """Create a FileSessionStorage instance for testing."""
        return FileSessionStorage(temp_dir)
    
    def test_file_storage_initialization(self, temp_dir):
        """Test FileSessionStorage initialization."""
        storage = FileSessionStorage(temp_dir)
        assert storage.storage_dir == Path(temp_dir)
        assert storage.storage_dir.exists()
    
    def test_set_and_get_session(self, storage):
        """Test setting and getting session data."""
        session_data = {"user_id": 123, "username": "testuser"}
        
        # Set session
        result = storage.set("session123", session_data)
        assert result is True
        
        # Get session
        retrieved = storage.get("session123")
        assert retrieved == session_data
    
    def test_set_with_ttl(self, storage):
        """Test setting session with TTL."""
        session_data = {"user_id": 123}
        
        # Set with 1 second TTL
        storage.set("session123", session_data, ttl_seconds=1)
        
        # Should be available immediately
        assert storage.get("session123") == session_data
        
        # Wait for expiry
        time.sleep(1.1)
        
        # Should be expired
        assert storage.get("session123") is None
    
    def test_delete_session(self, storage):
        """Test deleting session."""
        session_data = {"user_id": 123}
        storage.set("session123", session_data)
        
        # Verify it exists
        assert storage.get("session123") == session_data
        
        # Delete it
        result = storage.delete("session123")
        assert result is True
        
        # Verify it's gone
        assert storage.get("session123") is None
    
    def test_cleanup_expired(self, storage):
        """Test cleanup of expired sessions."""
        # Set sessions with different TTLs
        storage.set("session1", {"data": "1"}, ttl_seconds=1)
        storage.set("session2", {"data": "2"}, ttl_seconds=2)
        storage.set("session3", {"data": "3"})  # No TTL
        
        # Wait for first session to expire
        time.sleep(1.1)
        
        # Cleanup expired
        removed_count = storage.cleanup_expired()
        assert removed_count == 1
        
        # Verify correct sessions remain
        assert storage.get("session1") is None
        assert storage.get("session2") is not None
        assert storage.get("session3") is not None
    
    def test_corrupted_file_cleanup(self, storage, temp_dir):
        """Test cleanup of corrupted session files."""
        # Create a corrupted session file
        corrupted_file = Path(temp_dir) / "corrupted.json"
        corrupted_file.write_text("invalid json content")
        
        # Cleanup should remove corrupted file
        removed_count = storage.cleanup_expired()
        assert removed_count == 1
        assert not corrupted_file.exists()


class TestSessionHandler:
    """Test SessionHandler functionality."""
    
    @pytest.fixture
    def session_handler(self):
        """Create a SessionHandler instance for testing."""
        return SessionHandler(auto_cleanup=False)  # Disable auto cleanup for tests
    
    @pytest.fixture
    def file_session_handler(self):
        """Create a SessionHandler with file storage for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = FileSessionStorage(temp_dir)
            yield SessionHandler(storage=storage, auto_cleanup=False)
    
    def test_session_handler_initialization(self):
        """Test SessionHandler initialization."""
        handler = SessionHandler()
        
        assert isinstance(handler.storage, MemorySessionStorage)
        assert handler.session_header == "yaapp-session-id"
        assert handler.default_ttl == 3600
        assert handler.auto_cleanup is True
    
    def test_session_handler_custom_config(self):
        """Test SessionHandler with custom configuration."""
        storage = MemorySessionStorage()
        handler = SessionHandler(
            storage=storage,
            session_header="custom-session",
            default_ttl=7200,
            auto_cleanup=False
        )
        
        assert handler.storage is storage
        assert handler.session_header == "custom-session"
        assert handler.default_ttl == 7200
        assert handler.auto_cleanup is False
    
    def test_generate_session_id(self, session_handler):
        """Test session ID generation."""
        session_id1 = session_handler.generate_session_id()
        session_id2 = session_handler.generate_session_id()
        
        assert len(session_id1) == 32  # UUID without hyphens
        assert len(session_id2) == 32
        assert session_id1 != session_id2
        assert "-" not in session_id1
        assert "-" not in session_id2
    
    def test_create_session(self, session_handler):
        """Test session creation."""
        initial_data = {"user_id": 123, "role": "admin"}
        
        session_id = session_handler.create_session(initial_data)
        
        assert len(session_id) == 32
        
        # Retrieve session
        session_data = session_handler.get_session(session_id)
        assert session_data["user_id"] == 123
        assert session_data["role"] == "admin"
        assert "_created_at" in session_data
        assert "_last_accessed" in session_data
        assert session_data["_access_count"] == 1  # Incremented by get_session
    
    def test_create_session_with_custom_ttl(self, session_handler):
        """Test session creation with custom TTL."""
        # Test that TTL parameter is accepted and session is created
        session_id = session_handler.create_session({"data": "test"}, ttl_seconds=3600)
        
        # Should be available immediately
        session_data = session_handler.get_session(session_id)
        assert session_data is not None
        assert session_data["data"] == "test"
        
        # Test that session can be deleted
        result = session_handler.delete_session(session_id)
        assert result is True
        
        # Should be gone after deletion
        assert session_handler.get_session(session_id) is None
    
    def test_get_session_nonexistent(self, session_handler):
        """Test getting non-existent session."""
        result = session_handler.get_session("nonexistent")
        assert result is None
        
        # Test with empty session ID
        result = session_handler.get_session("")
        assert result is None
    
    def test_get_session_updates_access_metadata(self, session_handler):
        """Test that getting session updates access metadata."""
        session_id = session_handler.create_session({"data": "test"})
        
        # Get session multiple times
        session1 = session_handler.get_session(session_id)
        session2 = session_handler.get_session(session_id)
        
        assert session1["_access_count"] == 1
        assert session2["_access_count"] == 2
        assert session2["_last_accessed"] != session1["_last_accessed"]
    
    def test_update_session_merge(self, session_handler):
        """Test updating session with merge."""
        session_id = session_handler.create_session({"user_id": 123, "role": "user"})
        
        # Update with merge
        result = session_handler.update_session(
            session_id, 
            {"role": "admin", "permissions": ["read", "write"]}, 
            merge=True
        )
        assert result is True
        
        # Verify merged data
        session_data = session_handler.get_session(session_id)
        assert session_data["user_id"] == 123  # Original data preserved
        assert session_data["role"] == "admin"  # Updated
        assert session_data["permissions"] == ["read", "write"]  # Added
    
    def test_update_session_replace(self, session_handler):
        """Test updating session with replace."""
        session_id = session_handler.create_session({"user_id": 123, "role": "user"})
        
        # Update with replace
        result = session_handler.update_session(
            session_id, 
            {"role": "admin", "permissions": ["read", "write"]}, 
            merge=False
        )
        assert result is True
        
        # Verify replaced data
        session_data = session_handler.get_session(session_id)
        assert "user_id" not in session_data  # Original data removed
        assert session_data["role"] == "admin"
        assert session_data["permissions"] == ["read", "write"]
        assert "_created_at" in session_data  # Metadata added
    
    def test_update_session_nonexistent(self, session_handler):
        """Test updating non-existent session."""
        result = session_handler.update_session("nonexistent", {"data": "test"})
        assert result is False
        
        # Test with empty session ID
        result = session_handler.update_session("", {"data": "test"})
        assert result is False
    
    def test_delete_session(self, session_handler):
        """Test session deletion."""
        session_id = session_handler.create_session({"data": "test"})
        
        # Verify session exists
        assert session_handler.get_session(session_id) is not None
        
        # Delete session
        result = session_handler.delete_session(session_id)
        assert result is True
        
        # Verify session is gone
        assert session_handler.get_session(session_id) is None
        
        # Delete non-existent session
        result = session_handler.delete_session("nonexistent")
        assert result is False
    
    def test_extract_session_id_from_headers(self, session_handler):
        """Test extracting session ID from headers."""
        headers = {
            "Content-Type": "application/json",
            "yaapp-session-id": "session123",
            "User-Agent": "test"
        }
        
        session_id = session_handler.extract_session_id_from_headers(headers)
        assert session_id == "session123"
        
        # Test case-insensitive lookup
        headers_upper = {
            "YAAPP-SESSION-ID": "session456"
        }
        session_id = session_handler.extract_session_id_from_headers(headers_upper)
        assert session_id == "session456"
        
        # Test missing header
        headers_empty = {"Content-Type": "application/json"}
        session_id = session_handler.extract_session_id_from_headers(headers_empty)
        assert session_id is None
    
    def test_inject_session_id_to_headers(self, session_handler):
        """Test injecting session ID into headers."""
        existing_headers = {
            "Content-Type": "application/json",
            "User-Agent": "test"
        }
        
        updated_headers = session_handler.inject_session_id_to_headers(
            existing_headers, "session123"
        )
        
        assert updated_headers["Content-Type"] == "application/json"
        assert updated_headers["User-Agent"] == "test"
        assert updated_headers["yaapp-session-id"] == "session123"
        
        # Verify original headers not modified
        assert "yaapp-session-id" not in existing_headers
    
    def test_middleware_extract_session(self, session_handler):
        """Test middleware session extraction."""
        # Create session
        session_id = session_handler.create_session({"user_id": 123})
        
        # Test with valid session header
        headers = {"yaapp-session-id": session_id}
        session_data = session_handler.middleware_extract_session(headers)
        
        assert session_data is not None
        assert session_data["user_id"] == 123
        
        # Test with missing header
        headers_empty = {}
        session_data = session_handler.middleware_extract_session(headers_empty)
        assert session_data is None
        
        # Test with invalid session ID
        headers_invalid = {"yaapp-session-id": "invalid"}
        session_data = session_handler.middleware_extract_session(headers_invalid)
        assert session_data is None
    
    def test_middleware_create_response_headers(self, session_handler):
        """Test middleware response header creation."""
        # Test with no existing headers
        headers = session_handler.middleware_create_response_headers("session123")
        assert headers["yaapp-session-id"] == "session123"
        
        # Test with existing headers
        existing = {"Content-Type": "application/json"}
        headers = session_handler.middleware_create_response_headers(
            "session123", existing
        )
        assert headers["Content-Type"] == "application/json"
        assert headers["yaapp-session-id"] == "session123"
    
    def test_get_session_stats(self, session_handler):
        """Test getting session statistics."""
        # Create some sessions
        session_handler.create_session({"user": "1"})
        session_handler.create_session({"user": "2"})
        
        stats = session_handler.get_session_stats()
        
        assert stats["storage_type"] == "MemorySessionStorage"
        assert stats["session_header"] == "yaapp-session-id"
        assert stats["default_ttl"] == 3600
        assert stats["auto_cleanup"] is False
        assert stats["active_sessions"] == 2
    
    def test_auto_cleanup_thread(self):
        """Test automatic cleanup thread."""
        with patch('threading.Thread') as mock_thread:
            handler = SessionHandler(auto_cleanup=True)
            
            # Verify cleanup thread was started
            mock_thread.assert_called_once()
            thread_args = mock_thread.call_args
            assert thread_args[1]["daemon"] is True


class TestConvenienceFunctions:
    """Test convenience factory functions."""
    
    def test_create_memory_session_handler(self):
        """Test memory session handler factory."""
        handler = create_memory_session_handler(
            session_header="custom-header",
            default_ttl=7200
        )
        
        assert isinstance(handler.storage, MemorySessionStorage)
        assert handler.session_header == "custom-header"
        assert handler.default_ttl == 7200
    
    def test_create_file_session_handler(self):
        """Test file session handler factory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            handler = create_file_session_handler(
                storage_dir=temp_dir,
                session_header="file-session",
                default_ttl=1800
            )
            
            assert isinstance(handler.storage, FileSessionStorage)
            assert handler.session_header == "file-session"
            assert handler.default_ttl == 1800


class TestSessionIntegration:
    """Test session integration scenarios."""
    
    def test_full_session_lifecycle(self):
        """Test complete session lifecycle."""
        handler = SessionHandler(auto_cleanup=False)
        
        # 1. Create session
        session_id = handler.create_session({"user_id": 123, "role": "user"})
        
        # 2. Simulate HTTP request with session
        request_headers = {"yaapp-session-id": session_id}
        session_data = handler.middleware_extract_session(request_headers)
        assert session_data["user_id"] == 123
        
        # 3. Update session during request
        handler.update_session(session_id, {"last_action": "login"}, merge=True)
        
        # 4. Create response headers
        response_headers = handler.middleware_create_response_headers(session_id)
        assert response_headers["yaapp-session-id"] == session_id
        
        # 5. Verify updated session
        updated_session = handler.get_session(session_id)
        assert updated_session["user_id"] == 123
        assert updated_session["role"] == "user"
        assert updated_session["last_action"] == "login"
        
        # 6. Delete session (logout)
        result = handler.delete_session(session_id)
        assert result is True
        
        # 7. Verify session is gone
        assert handler.get_session(session_id) is None
    
    def test_session_expiry_workflow(self):
        """Test session expiry workflow."""
        handler = SessionHandler(default_ttl=1, auto_cleanup=False)
        
        # Create session with short TTL
        session_id = handler.create_session({"user_id": 123})
        
        # Should be available immediately
        assert handler.get_session(session_id) is not None
        
        # Wait for expiry
        time.sleep(1.1)
        
        # Should be expired
        assert handler.get_session(session_id) is None
        
        # Simulate request with expired session
        request_headers = {"yaapp-session-id": session_id}
        session_data = handler.middleware_extract_session(request_headers)
        assert session_data is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])