"""
Tests for FastAPI JSON/RPC API endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from api import app


class TestStorageAPI:
    """Test cases for storage API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Git Blockchain Storage API"
        assert "endpoints" in data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "storage" in data
    
    def test_store_and_retrieve_rest(self, client):
        """Test store and retrieve via REST API"""
        # Store data
        store_data = {
            "key": "test_user",
            "data": {"name": "Alice", "role": "admin"},
            "metadata": {"type": "user"}
        }
        
        response = client.post("/storage/store", json=store_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["data"]["key"] == "test_user"
        assert result["data"]["data"] == store_data["data"]
        assert "commit_hash" in result
        assert "blob_hash" in result
        
        # Retrieve data
        retrieve_data = {"key": "test_user"}
        response = client.post("/storage/retrieve", json=retrieve_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["data"]["key"] == "test_user"
        assert result["data"]["data"] == store_data["data"]
        assert result["data"]["metadata"] == store_data["metadata"]
    
    def test_retrieve_nonexistent_rest(self, client):
        """Test retrieving non-existent key via REST API"""
        retrieve_data = {"key": "nonexistent"}
        response = client.post("/storage/retrieve", json=retrieve_data)
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
    
    def test_delete_rest(self, client):
        """Test delete via REST API"""
        # Store data first
        store_data = {"key": "delete_test", "data": {"value": "to_delete"}}
        client.post("/storage/store", json=store_data)
        
        # Delete data
        delete_data = {"key": "delete_test"}
        response = client.post("/storage/delete", json=delete_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["data"]["deleted"] is True
        assert result["data"]["key"] == "delete_test"
    
    def test_list_keys_rest(self, client):
        """Test list keys via REST API"""
        # Store multiple items
        items = [
            {"key": "user_1", "data": {"name": "Alice"}},
            {"key": "user_2", "data": {"name": "Bob"}},
            {"key": "doc_1", "data": {"title": "Document"}}
        ]
        
        for item in items:
            client.post("/storage/store", json=item)
        
        # List all keys
        response = client.post("/storage/list", json={})
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert len(result["data"]) >= 3
        
        # List with prefix
        list_data = {"prefix": "user_"}
        response = client.post("/storage/list", json=list_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        user_keys = [key for key in result["data"] if key.startswith("user_")]
        assert len(user_keys) == 2
    
    def test_query_rest(self, client):
        """Test query via REST API"""
        # Store test data
        users = [
            {"key": "query_user_1", "data": {"name": "Alice", "role": "admin"}},
            {"key": "query_user_2", "data": {"name": "Bob", "role": "user"}},
            {"key": "query_user_3", "data": {"name": "Charlie", "role": "admin"}}
        ]
        
        for user in users:
            client.post("/storage/store", json=user)
        
        # Query by role
        query_data = {"filters": {"data.role": "admin"}}
        response = client.post("/storage/query", json=query_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert len(result["data"]) >= 2
        
        # Verify results
        admin_names = [item["data"]["name"] for item in result["data"]]
        assert "Alice" in admin_names
        assert "Charlie" in admin_names
    
    def test_history_rest(self, client):
        """Test history via REST API"""
        key = "history_test"
        
        # Store multiple versions
        versions = [
            {"key": key, "data": {"version": 1, "value": "first"}},
            {"key": key, "data": {"version": 2, "value": "second"}},
            {"key": key, "data": {"version": 3, "value": "third"}}
        ]
        
        for version in versions:
            client.post("/storage/store", json=version)
        
        # Get history
        history_data = {"key": key}
        response = client.post("/storage/history", json=history_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert len(result["data"]) == 3
        
        # Verify history order (newest first)
        versions_in_history = [item["data"]["data"]["version"] for item in result["data"]]
        assert versions_in_history == [3, 2, 1]
    
    def test_stats_rest(self, client):
        """Test stats via REST API"""
        response = client.get("/storage/stats")
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert "total_commits" in result["data"]
        assert "total_objects" in result["data"]
        assert "repository_path" in result["data"]


class TestIssueAPI:
    """Test cases for issue management API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_create_issue_rest(self, client):
        """Test creating issue via REST API"""
        issue_data = {
            "title": "Test Issue",
            "description": "This is a test issue",
            "assignee": "alice@example.com"
        }
        
        response = client.post("/issues/create", json=issue_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["data"]["data"]["title"] == "Test Issue"
        assert result["data"]["data"]["assignee"] == "alice@example.com"
        assert result["data"]["data"]["status"] == "open"
        
        return result["data"]["data"]["id"]  # Return issue ID for other tests
    
    def test_get_issue_rest(self, client):
        """Test getting issue via REST API"""
        # Create issue first
        issue_id = self.test_create_issue_rest(client)
        
        # Get issue
        response = client.get(f"/issues/{issue_id}")
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["data"]["data"]["id"] == issue_id
        assert result["data"]["data"]["title"] == "Test Issue"
    
    def test_update_issue_rest(self, client):
        """Test updating issue via REST API"""
        # Create issue first
        issue_id = self.test_create_issue_rest(client)
        
        # Update issue
        update_data = {
            "issue_id": issue_id,
            "title": "Updated Title",
            "status": "in_progress"
        }
        
        response = client.post("/issues/update", json=update_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["data"]["data"]["title"] == "Updated Title"
        assert result["data"]["data"]["status"] == "in_progress"
    
    def test_request_review_rest(self, client):
        """Test requesting review via REST API"""
        # Create issue first
        issue_id = self.test_create_issue_rest(client)
        
        # Request review
        review_data = {
            "issue_id": issue_id,
            "reviewer": "reviewer@example.com"
        }
        
        response = client.post("/issues/request-review", json=review_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["data"]["data"]["issue_id"] == issue_id
        assert result["data"]["data"]["reviewer"] == "reviewer@example.com"
        assert result["data"]["data"]["status"] == "pending"
        
        return result["data"]["data"]["id"]  # Return review ID
    
    def test_submit_review_rest(self, client):
        """Test submitting review via REST API"""
        # Create issue and request review
        issue_id = self.test_create_issue_rest(client)
        review_id = self.test_request_review_rest(client)
        
        # Submit review
        submit_data = {
            "review_id": review_id,
            "status": "approved",
            "comments": ["Looks good!", "LGTM"],
            "decision_notes": "Approved with suggestions"
        }
        
        response = client.post("/issues/submit-review", json=submit_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["data"]["data"]["status"] == "approved"
        assert result["data"]["data"]["comments"] == ["Looks good!", "LGTM"]
    
    def test_list_issues_rest(self, client):
        """Test listing issues via REST API"""
        # Create multiple issues
        for i in range(3):
            issue_data = {
                "title": f"Issue {i+1}",
                "description": f"Description {i+1}"
            }
            client.post("/issues/create", json=issue_data)
        
        # List all issues
        response = client.post("/issues/list", json={})
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert len(result["data"]) >= 3
    
    def test_list_reviews_rest(self, client):
        """Test listing reviews via REST API"""
        # Create issue and reviews
        issue_id = self.test_create_issue_rest(client)
        
        # Create multiple reviews
        reviewers = ["reviewer1@example.com", "reviewer2@example.com"]
        for reviewer in reviewers:
            review_data = {"issue_id": issue_id, "reviewer": reviewer}
            client.post("/issues/request-review", json=review_data)
        
        # List all reviews
        response = client.post("/reviews/list", json={})
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert len(result["data"]) >= 2


class TestRPCAPI:
    """Test cases for JSON-RPC API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_rpc_storage_store(self, client):
        """Test storage.store via RPC"""
        rpc_request = {
            "method": "storage.store",
            "params": {
                "key": "rpc_test",
                "data": {"name": "RPC Test", "value": 42},
                "metadata": {"type": "test"}
            },
            "id": "test_1"
        }
        
        response = client.post("/rpc", json=rpc_request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["error"] is None
        assert result["id"] == "test_1"
        assert result["result"]["data"]["key"] == "rpc_test"
        assert "commit_hash" in result["result"]
    
    def test_rpc_storage_retrieve(self, client):
        """Test storage.retrieve via RPC"""
        # Store data first
        store_request = {
            "method": "storage.store",
            "params": {"key": "rpc_retrieve_test", "data": {"value": "test"}},
            "id": "store_1"
        }
        client.post("/rpc", json=store_request)
        
        # Retrieve data
        retrieve_request = {
            "method": "storage.retrieve",
            "params": {"key": "rpc_retrieve_test"},
            "id": "retrieve_1"
        }
        
        response = client.post("/rpc", json=retrieve_request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["error"] is None
        assert result["id"] == "retrieve_1"
        assert result["result"]["data"]["key"] == "rpc_retrieve_test"
        assert result["result"]["data"]["data"]["value"] == "test"
    
    def test_rpc_storage_list(self, client):
        """Test storage.list via RPC"""
        # Store some data first
        for i in range(3):
            store_request = {
                "method": "storage.store",
                "params": {"key": f"rpc_list_{i}", "data": {"index": i}},
                "id": f"store_{i}"
            }
            client.post("/rpc", json=store_request)
        
        # List keys
        list_request = {
            "method": "storage.list",
            "params": {"prefix": "rpc_list_"},
            "id": "list_1"
        }
        
        response = client.post("/rpc", json=list_request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["error"] is None
        assert result["id"] == "list_1"
        assert len(result["result"]["data"]) >= 3
    
    def test_rpc_issues_create(self, client):
        """Test issues.create via RPC"""
        rpc_request = {
            "method": "issues.create",
            "params": {
                "title": "RPC Issue",
                "description": "Created via RPC",
                "assignee": "rpc@example.com"
            },
            "id": "issue_1"
        }
        
        response = client.post("/rpc", json=rpc_request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["error"] is None
        assert result["id"] == "issue_1"
        assert result["result"]["data"]["data"]["title"] == "RPC Issue"
        assert result["result"]["data"]["data"]["assignee"] == "rpc@example.com"
        
        return result["result"]["data"]["data"]["id"]
    
    def test_rpc_issues_get(self, client):
        """Test issues.get via RPC"""
        # Create issue first
        issue_id = self.test_rpc_issues_create(client)
        
        # Get issue
        get_request = {
            "method": "issues.get",
            "params": {"issue_id": issue_id},
            "id": "get_1"
        }
        
        response = client.post("/rpc", json=get_request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["error"] is None
        assert result["result"]["data"]["data"]["id"] == issue_id
        assert result["result"]["data"]["data"]["title"] == "RPC Issue"
    
    def test_rpc_issues_request_review(self, client):
        """Test issues.request_review via RPC"""
        # Create issue first
        issue_id = self.test_rpc_issues_create(client)
        
        # Request review
        review_request = {
            "method": "issues.request_review",
            "params": {
                "issue_id": issue_id,
                "reviewer": "rpc_reviewer@example.com"
            },
            "id": "review_1"
        }
        
        response = client.post("/rpc", json=review_request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["error"] is None
        assert result["result"]["data"]["data"]["issue_id"] == issue_id
        assert result["result"]["data"]["data"]["reviewer"] == "rpc_reviewer@example.com"
        
        return result["result"]["data"]["data"]["id"]
    
    def test_rpc_issues_submit_review(self, client):
        """Test issues.submit_review via RPC"""
        # Create issue and request review
        issue_id = self.test_rpc_issues_create(client)
        review_id = self.test_rpc_issues_request_review(client)
        
        # Submit review
        submit_request = {
            "method": "issues.submit_review",
            "params": {
                "review_id": review_id,
                "status": "approved",
                "comments": ["RPC approval"],
                "decision_notes": "Approved via RPC"
            },
            "id": "submit_1"
        }
        
        response = client.post("/rpc", json=submit_request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["error"] is None
        assert result["result"]["data"]["data"]["status"] == "approved"
        assert result["result"]["data"]["data"]["comments"] == ["RPC approval"]
    
    def test_rpc_unknown_method(self, client):
        """Test RPC with unknown method"""
        rpc_request = {
            "method": "unknown.method",
            "params": {},
            "id": "unknown_1"
        }
        
        response = client.post("/rpc", json=rpc_request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["error"] is not None
        assert "Unknown method" in result["error"]
        assert result["id"] == "unknown_1"
    
    def test_rpc_error_handling(self, client):
        """Test RPC error handling"""
        # Try to retrieve non-existent key
        rpc_request = {
            "method": "storage.retrieve",
            "params": {"key": "nonexistent_rpc_key"},
            "id": "error_1"
        }
        
        response = client.post("/rpc", json=rpc_request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["error"] is not None
        assert "not found" in result["error"].lower()
        assert result["id"] == "error_1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])