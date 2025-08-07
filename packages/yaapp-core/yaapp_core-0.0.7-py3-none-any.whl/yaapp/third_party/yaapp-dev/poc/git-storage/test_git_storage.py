"""
Tests for Git-based blockchain storage implementation.
"""

import json
import tempfile
import pytest
from pathlib import Path

from git_storage import GitBlockchainStorage, IssueManager, Issue, Review


class TestGitBlockchainStorage:
    """Test cases for GitBlockchainStorage"""
    
    @pytest.fixture
    def storage(self):
        """Create temporary storage for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield GitBlockchainStorage(tmpdir)
    
    def test_store_and_retrieve(self, storage):
        """Test basic store and retrieve operations"""
        # Store data
        test_data = {"name": "Alice", "role": "admin", "age": 30}
        result = storage.store("user_alice", test_data)
        
        assert result.success
        assert result.data['key'] == "user_alice"
        assert result.data['data'] == test_data
        assert result.commit_hash is not None
        assert result.blob_hash is not None
        
        # Retrieve data
        result = storage.retrieve("user_alice")
        
        assert result.success
        assert result.data['key'] == "user_alice"
        assert result.data['data'] == test_data
        assert 'timestamp' in result.data
    
    def test_store_with_metadata(self, storage):
        """Test storing data with metadata"""
        test_data = {"title": "Test Document"}
        metadata = {"type": "document", "author": "test_user"}
        
        result = storage.store("doc_1", test_data, metadata)
        
        assert result.success
        assert result.data['metadata'] == metadata
        
        # Retrieve and verify metadata
        result = storage.retrieve("doc_1")
        assert result.success
        assert result.data['metadata'] == metadata
    
    def test_retrieve_nonexistent_key(self, storage):
        """Test retrieving non-existent key"""
        result = storage.retrieve("nonexistent_key")
        
        assert not result.success
        assert "not found" in result.error.lower()
    
    def test_delete_operation(self, storage):
        """Test delete operation creates tombstone"""
        # Store data first
        test_data = {"value": "test"}
        storage.store("test_key", test_data)
        
        # Delete data
        result = storage.delete("test_key")
        
        assert result.success
        assert result.data['deleted'] is True
        assert result.data['key'] == "test_key"
        
        # Verify tombstone was created
        tombstone_result = storage.retrieve("_deleted_test_key")
        assert tombstone_result.success
        assert tombstone_result.data['data']['deleted'] is True
    
    def test_list_keys(self, storage):
        """Test listing keys"""
        # Store multiple items
        test_items = {
            "user_1": {"name": "Alice"},
            "user_2": {"name": "Bob"},
            "doc_1": {"title": "Document 1"}
        }
        
        for key, data in test_items.items():
            storage.store(key, data)
        
        # List all keys
        result = storage.list_keys()
        
        assert result.success
        assert len(result.data) == 3
        assert all(key in result.data for key in test_items.keys())
    
    def test_list_keys_with_prefix(self, storage):
        """Test listing keys with prefix filter"""
        # Store items with different prefixes
        items = {
            "user_alice": {"name": "Alice"},
            "user_bob": {"name": "Bob"},
            "doc_readme": {"title": "README"}
        }
        
        for key, data in items.items():
            storage.store(key, data)
        
        # List keys with prefix
        result = storage.list_keys(prefix="user_")
        
        assert result.success
        assert len(result.data) == 2
        assert "user_alice" in result.data
        assert "user_bob" in result.data
        assert "doc_readme" not in result.data
    
    def test_query_operations(self, storage):
        """Test query functionality"""
        # Store test data
        users = [
            {"name": "Alice", "role": "admin", "age": 30},
            {"name": "Bob", "role": "user", "age": 25},
            {"name": "Charlie", "role": "admin", "age": 35}
        ]
        
        for i, user in enumerate(users):
            storage.store(f"user_{i}", user, {"type": "user"})
        
        # Query by role
        result = storage.query({"data.role": "admin"})
        
        assert result.success
        assert len(result.data) == 2
        
        # Verify results
        admin_names = [item['data']['name'] for item in result.data]
        assert "Alice" in admin_names
        assert "Charlie" in admin_names
        assert "Bob" not in admin_names
    
    def test_query_with_range_filters(self, storage):
        """Test query with range filters"""
        # Store users with different ages
        users = [
            {"name": "Young", "age": 20},
            {"name": "Middle", "age": 30},
            {"name": "Old", "age": 40}
        ]
        
        for i, user in enumerate(users):
            storage.store(f"user_{i}", user)
        
        # Query for users older than 25
        result = storage.query({"data.age": {"$gt": 25}})
        
        assert result.success
        assert len(result.data) == 2
        
        names = [item['data']['name'] for item in result.data]
        assert "Middle" in names
        assert "Old" in names
        assert "Young" not in names
    
    def test_get_history(self, storage):
        """Test getting history of a key"""
        key = "test_key"
        
        # Store initial version
        storage.store(key, {"version": 1, "value": "initial"})
        
        # Update multiple times
        storage.store(key, {"version": 2, "value": "updated"})
        storage.store(key, {"version": 3, "value": "final"})
        
        # Get history
        result = storage.get_history(key)
        
        assert result.success
        assert len(result.data) == 3
        
        # Verify history order (newest first)
        versions = [item['data']['data']['version'] for item in result.data]
        assert versions == [3, 2, 1]
    
    def test_get_stats(self, storage):
        """Test getting storage statistics"""
        # Store some data
        storage.store("test1", {"data": "value1"})
        storage.store("test2", {"data": "value2"})
        
        result = storage.get_stats()
        
        assert result.success
        assert 'total_commits' in result.data
        assert 'total_objects' in result.data
        assert 'repository_path' in result.data
        assert result.data['total_commits'] >= 3  # Initial + 2 data commits
    
    def test_caching(self, storage):
        """Test that caching works correctly"""
        # Store data
        test_data = {"cached": True}
        storage.store("cache_test", test_data)
        
        # First retrieval (from storage)
        result1 = storage.retrieve("cache_test")
        assert result1.success
        
        # Second retrieval (should be from cache)
        result2 = storage.retrieve("cache_test")
        assert result2.success
        assert result2.data == result1.data
        
        # Verify cache contains the key
        assert "cache_test" in storage._cache


class TestIssueManager:
    """Test cases for IssueManager"""
    
    @pytest.fixture
    def issue_manager(self):
        """Create temporary issue manager for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = GitBlockchainStorage(tmpdir)
            yield IssueManager(storage)
    
    def test_create_issue(self, issue_manager):
        """Test creating an issue"""
        result = issue_manager.create_issue(
            title="Test Issue",
            description="This is a test issue",
            assignee="alice@example.com"
        )
        
        assert result.success
        assert result.data['data']['title'] == "Test Issue"
        assert result.data['data']['description'] == "This is a test issue"
        assert result.data['data']['assignee'] == "alice@example.com"
        assert result.data['data']['status'] == "open"
        assert result.data['metadata']['type'] == "issue"
    
    def test_get_issue(self, issue_manager):
        """Test getting an issue"""
        # Create issue first
        create_result = issue_manager.create_issue("Test Issue", "Description")
        issue_id = create_result.data['data']['id']
        
        # Get issue
        result = issue_manager.get_issue(issue_id)
        
        assert result.success
        assert result.data['data']['id'] == issue_id
        assert result.data['data']['title'] == "Test Issue"
    
    def test_update_issue(self, issue_manager):
        """Test updating an issue"""
        # Create issue
        create_result = issue_manager.create_issue("Original Title", "Original Description")
        issue_id = create_result.data['data']['id']
        
        # Update issue
        result = issue_manager.update_issue(
            issue_id,
            title="Updated Title",
            status="in_progress"
        )
        
        assert result.success
        assert result.data['data']['title'] == "Updated Title"
        assert result.data['data']['status'] == "in_progress"
        assert result.data['data']['description'] == "Original Description"  # Unchanged
    
    def test_request_review(self, issue_manager):
        """Test requesting review for an issue"""
        # Create issue
        create_result = issue_manager.create_issue("Review Test", "Needs review")
        issue_id = create_result.data['data']['id']
        
        # Request review
        result = issue_manager.request_review(issue_id, "reviewer@example.com")
        
        assert result.success
        assert result.data['data']['issue_id'] == issue_id
        assert result.data['data']['reviewer'] == "reviewer@example.com"
        assert result.data['data']['status'] == "pending"
        assert result.data['metadata']['type'] == "review"
        
        # Verify issue was updated
        issue_result = issue_manager.get_issue(issue_id)
        assert issue_result.data['data']['status'] == "under_review"
        assert issue_result.data['data']['review_status'] == "pending"
    
    def test_submit_review_approved(self, issue_manager):
        """Test submitting an approved review"""
        # Create issue and request review
        create_result = issue_manager.create_issue("Review Test", "Needs review")
        issue_id = create_result.data['data']['id']
        
        review_result = issue_manager.request_review(issue_id, "reviewer@example.com")
        review_id = review_result.data['data']['id']
        
        # Submit approved review
        result = issue_manager.submit_review(
            review_id,
            status="approved",
            comments=["Looks good!", "LGTM"],
            decision_notes="Approved with minor suggestions"
        )
        
        assert result.success
        assert result.data['data']['status'] == "approved"
        assert result.data['data']['comments'] == ["Looks good!", "LGTM"]
        assert result.data['data']['decision_notes'] == "Approved with minor suggestions"
        assert result.data['data']['approved_at'] is not None
        
        # Verify issue was updated
        issue_result = issue_manager.get_issue(issue_id)
        assert issue_result.data['data']['review_status'] == "approved"
        assert issue_result.data['data']['status'] == "approved"
    
    def test_submit_review_rejected(self, issue_manager):
        """Test submitting a rejected review"""
        # Create issue and request review
        create_result = issue_manager.create_issue("Review Test", "Needs review")
        issue_id = create_result.data['data']['id']
        
        review_result = issue_manager.request_review(issue_id, "reviewer@example.com")
        review_id = review_result.data['data']['id']
        
        # Submit rejected review
        result = issue_manager.submit_review(
            review_id,
            status="rejected",
            comments=["Needs more work"],
            decision_notes="Please address the security concerns"
        )
        
        assert result.success
        assert result.data['data']['status'] == "rejected"
        
        # Verify issue was updated
        issue_result = issue_manager.get_issue(issue_id)
        assert issue_result.data['data']['review_status'] == "rejected"
        assert issue_result.data['data']['status'] == "needs_changes"
    
    def test_list_issues(self, issue_manager):
        """Test listing issues"""
        # Create multiple issues
        issue_manager.create_issue("Issue 1", "Description 1")
        issue_manager.create_issue("Issue 2", "Description 2")
        
        # Update one issue status
        create_result = issue_manager.create_issue("Issue 3", "Description 3")
        issue_id = create_result.data['data']['id']
        issue_manager.update_issue(issue_id, status="closed")
        
        # List all issues
        result = issue_manager.list_issues()
        assert result.success
        assert len(result.data) == 3
        
        # List only open issues
        result = issue_manager.list_issues(status="open")
        assert result.success
        assert len(result.data) == 2
        
        # List only closed issues
        result = issue_manager.list_issues(status="closed")
        assert result.success
        assert len(result.data) == 1
    
    def test_list_reviews(self, issue_manager):
        """Test listing reviews"""
        # Create issues and reviews
        create_result1 = issue_manager.create_issue("Issue 1", "Description 1")
        issue_id1 = create_result1.data['data']['id']
        
        create_result2 = issue_manager.create_issue("Issue 2", "Description 2")
        issue_id2 = create_result2.data['data']['id']
        
        # Create reviews
        issue_manager.request_review(issue_id1, "reviewer1@example.com")
        issue_manager.request_review(issue_id1, "reviewer2@example.com")
        issue_manager.request_review(issue_id2, "reviewer1@example.com")
        
        # List all reviews
        result = issue_manager.list_reviews()
        assert result.success
        assert len(result.data) == 3
        
        # List reviews for specific issue
        result = issue_manager.list_reviews(issue_id=issue_id1)
        assert result.success
        assert len(result.data) == 2
        
        # Verify all reviews are for the correct issue
        for review in result.data:
            assert review['data']['issue_id'] == issue_id1
    
    def test_complete_workflow(self, issue_manager):
        """Test complete issue workflow from creation to approval"""
        # 1. Create issue
        create_result = issue_manager.create_issue(
            title="Complete Workflow Test",
            description="Testing the complete workflow",
            assignee="developer@example.com"
        )
        issue_id = create_result.data['data']['id']
        
        # 2. Request review
        review_result = issue_manager.request_review(issue_id, "reviewer@example.com")
        review_id = review_result.data['data']['id']
        
        # 3. Submit review
        issue_manager.submit_review(
            review_id,
            status="approved",
            comments=["Great work!"],
            decision_notes="Approved for deployment"
        )
        
        # 4. Verify final state
        final_issue = issue_manager.get_issue(issue_id)
        assert final_issue.data['data']['status'] == "approved"
        assert final_issue.data['data']['review_status'] == "approved"
        
        final_review = issue_manager.storage.retrieve(review_id)
        assert final_review.data['data']['status'] == "approved"
        assert final_review.data['data']['comments'] == ["Great work!"]
        
        # 5. Verify history tracking
        history_result = issue_manager.storage.get_history(issue_id)
        assert history_result.success
        assert len(history_result.data) >= 3  # Create, request review, approve


if __name__ == "__main__":
    pytest.main([__file__, "-v"])