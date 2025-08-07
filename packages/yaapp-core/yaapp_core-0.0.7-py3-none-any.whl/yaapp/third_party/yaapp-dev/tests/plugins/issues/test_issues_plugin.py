"""
Tests for the Issues plugin.
"""

# import pytest  # Removed for compatibility
from datetime import datetime
from yaapp import Yaapp
from yaapp.plugins.storage.plugin import Storage
from yaapp.plugins.issues.plugin import Issues as IssuesPlugin
from yaapp.result import Result


class TestIssuesPlugin:
    """Test suite for Issues plugin functionality."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.yaapp = Yaapp(auto_discover=False)
        
        # Set up storage
        storage = Storage({'backend': 'memory'})
        storage_result = self.yaapp.expose(storage, name="storage")
        # The expose method returns the original object when successful
        assert storage_result is not None
        
        # Set up issues plugin
        self.issues = IssuesPlugin()
        self.issues.yaapp = self.yaapp  # Set yaapp instance
        issues_result = self.yaapp.expose(self.issues, name="issues")
        assert issues_result is not None
    
    def test_create_issue(self):
        """Test creating a new issue."""
        result = self.issues.create(
            title="Test Issue",
            description="This is a test issue",
            reporter="test@example.com",
            priority="medium"
        )
        
        assert result.is_ok()
        issue_id = result.unwrap()
        assert issue_id.startswith("issue_")
    
    def test_get_issue(self):
        """Test retrieving an issue."""
        # Create an issue first
        create_result = self.issues.create(
            title="Test Issue",
            description="This is a test issue", 
            reporter="test@example.com"
        )
        assert create_result.is_ok()
        issue_id = create_result.unwrap()
        
        # Get the issue
        get_result = self.issues.get(issue_id)
        assert get_result.is_ok()
        
        issue = get_result.unwrap()
        assert issue is not None
        assert issue["title"] == "Test Issue"
        assert issue["description"] == "This is a test issue"
        assert issue["reporter"] == "test@example.com"
        assert issue["status"] == "open"
        assert issue["priority"] == "medium"
    
    def test_get_nonexistent_issue(self):
        """Test getting an issue that doesn't exist."""
        result = self.issues.get("nonexistent_id")
        assert result.is_ok()
        assert result.unwrap() is None
    
    def test_update_issue(self):
        """Test updating an issue."""
        # Create an issue first
        create_result = self.issues.create(
            title="Test Issue",
            description="Original description",
            reporter="test@example.com"
        )
        assert create_result.is_ok()
        issue_id = create_result.unwrap()
        
        # Update the issue
        update_result = self.issues.update(
            issue_id,
            description="Updated description",
            priority="high"
        )
        assert update_result.is_ok()
        assert update_result.unwrap() is True
        
        # Verify the update
        get_result = self.issues.get(issue_id)
        assert get_result.is_ok()
        
        issue = get_result.unwrap()
        assert issue["description"] == "Updated description"
        assert issue["priority"] == "high"
        assert issue["title"] == "Test Issue"  # Unchanged
    
    def test_update_nonexistent_issue(self):
        """Test updating an issue that doesn't exist."""
        result = self.issues.update("nonexistent_id", description="New description")
        assert not result.is_ok()
    
    def test_delete_issue(self):
        """Test deleting an issue."""
        # Create an issue first
        create_result = self.issues.create(
            title="Test Issue",
            description="To be deleted",
            reporter="test@example.com"
        )
        assert create_result.is_ok()
        issue_id = create_result.unwrap()
        
        # Delete the issue
        delete_result = self.issues.delete(issue_id)
        assert delete_result.is_ok()
        
        # Verify it's gone
        get_result = self.issues.get(issue_id)
        assert get_result.is_ok()
        assert get_result.unwrap() is None
    
    def test_list_issues(self):
        """Test listing issues."""
        # Create multiple issues
        issue1_result = self.issues.create(
            title="Issue 1",
            description="First issue",
            reporter="user1@example.com",
            priority="high"
        )
        issue2_result = self.issues.create(
            title="Issue 2", 
            description="Second issue",
            reporter="user2@example.com",
            priority="low",
            assignee="dev@example.com"
        )
        
        assert issue1_result.is_ok()
        assert issue2_result.is_ok()
        
        # List all issues
        list_result = self.issues.list()
        assert list_result.is_ok()
        
        issues = list_result.unwrap()
        assert len(issues) == 2
        
        # Check sorting (newest first)
        assert issues[0]["title"] == "Issue 2"
        assert issues[1]["title"] == "Issue 1"
    
    def test_list_issues_with_status_filter(self):
        """Test listing issues with status filter."""
        # Create issues with different statuses
        issue1_result = self.issues.create(
            title="Open Issue",
            description="This is open",
            reporter="test@example.com"
        )
        issue2_result = self.issues.create(
            title="Closed Issue",
            description="This will be closed",
            reporter="test@example.com"
        )
        
        assert issue1_result.is_ok()
        assert issue2_result.is_ok()
        
        # Close one issue
        issue2_id = issue2_result.unwrap()
        close_result = self.issues.close(issue2_id)
        assert close_result.is_ok()
        
        # List only open issues
        open_result = self.issues.list(status="open")
        assert open_result.is_ok()
        
        open_issues = open_result.unwrap()
        assert len(open_issues) == 1
        assert open_issues[0]["title"] == "Open Issue"
        assert open_issues[0]["status"] == "open"
    
    def test_list_issues_with_assignee_filter(self):
        """Test listing issues with assignee filter."""
        # Create issues with different assignees
        issue1_result = self.issues.create(
            title="Assigned Issue",
            description="This is assigned",
            reporter="test@example.com",
            assignee="dev1@example.com"
        )
        issue2_result = self.issues.create(
            title="Unassigned Issue",
            description="This is unassigned",
            reporter="test@example.com"
        )
        
        assert issue1_result.is_ok()
        assert issue2_result.is_ok()
        
        # List issues for specific assignee
        assigned_result = self.issues.list(assignee="dev1@example.com")
        assert assigned_result.is_ok()
        
        assigned_issues = assigned_result.unwrap()
        assert len(assigned_issues) == 1
        assert assigned_issues[0]["title"] == "Assigned Issue"
        assert assigned_issues[0]["assignee"] == "dev1@example.com"
    
    def test_assign_issue(self):
        """Test assigning an issue."""
        # Create an issue
        create_result = self.issues.create(
            title="Test Issue",
            description="To be assigned",
            reporter="test@example.com"
        )
        assert create_result.is_ok()
        issue_id = create_result.unwrap()
        
        # Assign the issue
        assign_result = self.issues.assign(issue_id, "dev@example.com")
        assert assign_result.is_ok()
        
        # Verify assignment
        get_result = self.issues.get(issue_id)
        assert get_result.is_ok()
        
        issue = get_result.unwrap()
        assert issue["assignee"] == "dev@example.com"
    
    def test_close_issue(self):
        """Test closing an issue."""
        # Create an issue
        create_result = self.issues.create(
            title="Test Issue",
            description="To be closed",
            reporter="test@example.com"
        )
        assert create_result.is_ok()
        issue_id = create_result.unwrap()
        
        # Close the issue
        close_result = self.issues.close(issue_id, resolution="completed")
        assert close_result.is_ok()
        
        # Verify closure
        get_result = self.issues.get(issue_id)
        assert get_result.is_ok()
        
        issue = get_result.unwrap()
        assert issue["status"] == "closed"
        assert issue["resolution"] == "completed"
    
    def test_reopen_issue(self):
        """Test reopening a closed issue."""
        # Create and close an issue
        create_result = self.issues.create(
            title="Test Issue",
            description="To be reopened",
            reporter="test@example.com"
        )
        assert create_result.is_ok()
        issue_id = create_result.unwrap()
        
        close_result = self.issues.close(issue_id)
        assert close_result.is_ok()
        
        # Reopen the issue
        reopen_result = self.issues.reopen(issue_id)
        assert reopen_result.is_ok()
        
        # Verify reopening
        get_result = self.issues.get(issue_id)
        assert get_result.is_ok()
        
        issue = get_result.unwrap()
        assert issue["status"] == "open"
    
    def test_add_comment(self):
        """Test adding a comment to an issue."""
        # Create an issue
        create_result = self.issues.create(
            title="Test Issue",
            description="For commenting",
            reporter="test@example.com"
        )
        assert create_result.is_ok()
        issue_id = create_result.unwrap()
        
        # Add a comment
        comment_result = self.issues.add_comment(
            issue_id,
            "This is a test comment",
            "commenter@example.com"
        )
        assert comment_result.is_ok()
        
        # Verify comment was added
        get_result = self.issues.get(issue_id)
        assert get_result.is_ok()
        
        issue = get_result.unwrap()
        assert "comments" in issue
        assert len(issue["comments"]) == 1
        
        comment = issue["comments"][0]
        assert comment["text"] == "This is a test comment"
        assert comment["author"] == "commenter@example.com"
        assert comment["id"].startswith("comment_")
    
    def test_get_comments(self):
        """Test getting comments for an issue."""
        # Create an issue
        create_result = self.issues.create(
            title="Test Issue",
            description="For commenting",
            reporter="test@example.com"
        )
        assert create_result.is_ok()
        issue_id = create_result.unwrap()
        
        # Add multiple comments
        self.issues.add_comment(issue_id, "First comment", "user1@example.com")
        self.issues.add_comment(issue_id, "Second comment", "user2@example.com")
        
        # Get comments
        comments_result = self.issues.get_comments(issue_id)
        assert comments_result.is_ok()
        
        comments = comments_result.unwrap()
        assert len(comments) == 2
        assert comments[0]["text"] == "First comment"
        assert comments[1]["text"] == "Second comment"
    
    def test_add_comment_to_nonexistent_issue(self):
        """Test adding a comment to a nonexistent issue."""
        result = self.issues.add_comment(
            "nonexistent_id",
            "This should fail",
            "user@example.com"
        )
        assert not result.is_ok()
    
    def test_get_comments_for_nonexistent_issue(self):
        """Test getting comments for a nonexistent issue."""
        result = self.issues.get_comments("nonexistent_id")
        assert not result.is_ok()
    
    def test_issue_timestamps(self):
        """Test that issues have proper timestamps."""
        # Create an issue
        create_result = self.issues.create(
            title="Test Issue",
            description="For timestamp testing",
            reporter="test@example.com"
        )
        assert create_result.is_ok()
        issue_id = create_result.unwrap()
        
        # Get the issue and check timestamps
        get_result = self.issues.get(issue_id)
        assert get_result.is_ok()
        
        issue = get_result.unwrap()
        assert "created_at" in issue
        assert "updated_at" in issue
        
        # Parse timestamps to ensure they're valid
        created_at = datetime.fromisoformat(issue["created_at"])
        updated_at = datetime.fromisoformat(issue["updated_at"])
        
        assert created_at <= updated_at
    
    def test_issue_id_format(self):
        """Test that issue IDs have the correct format."""
        create_result = self.issues.create(
            title="Test Issue",
            description="For ID testing",
            reporter="test@example.com"
        )
        assert create_result.is_ok()
        
        issue_id = create_result.unwrap()
        assert issue_id.startswith("issue_")
        assert len(issue_id) == 14  # "issue_" + 8 hex chars
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        create_result = self.issues.create(
            title="Test Issue",
            description="For default testing",
            reporter="test@example.com"
        )
        assert create_result.is_ok()
        issue_id = create_result.unwrap()
        
        get_result = self.issues.get(issue_id)
        assert get_result.is_ok()
        
        issue = get_result.unwrap()
        assert issue["status"] == "open"
        assert issue["priority"] == "medium"
        assert issue["assignee"] is None