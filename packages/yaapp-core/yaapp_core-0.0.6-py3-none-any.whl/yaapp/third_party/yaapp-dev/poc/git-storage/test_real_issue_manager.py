#!/usr/bin/env python3
"""
Tests for the real Git-based issue management system.
"""

import tempfile
import pytest
from pathlib import Path

from real_issue_manager import GitIssueManager, Issue, Review


class TestRealGitIssueManager:
    """Test cases for real Git-based issue management"""
    
    @pytest.fixture
    def issue_manager(self):
        """Create temporary issue manager for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "test_repo"
            yield GitIssueManager(str(repo_path))
    
    def test_repository_initialization(self, issue_manager):
        """Test that Git repository is properly initialized"""
        repo_path = issue_manager.repo_path
        
        # Check Git repository exists
        assert (repo_path / ".git").exists()
        
        # Check directory structure
        assert issue_manager.issues_dir.exists()
        assert issue_manager.reviews_dir.exists()
        assert issue_manager.metadata_dir.exists()
        
        # Check initial commit exists
        result = issue_manager._run_git_command(["log", "--oneline"])
        assert "Initial commit" in result.stdout
    
    def test_create_issue(self, issue_manager):
        """Test creating an issue"""
        issue = issue_manager.create_issue(
            title="Test Issue",
            description="This is a test issue",
            assignee="test@example.com",
            labels=["test", "bug"]
        )
        
        assert issue.title == "Test Issue"
        assert issue.description == "This is a test issue"
        assert issue.assignee == "test@example.com"
        assert issue.labels == ["test", "bug"]
        assert issue.status == "open"
        assert issue.review_status == "not_required"
        
        # Verify issue file exists
        issue_file = issue_manager.issues_dir / f"{issue.id}.json"
        assert issue_file.exists()
        
        # Verify Git commit was created
        result = issue_manager._run_git_command(["log", "--oneline", "-1"])
        assert "Issue: Test Issue" in result.stdout
    
    def test_get_issue(self, issue_manager):
        """Test retrieving an issue"""
        # Create issue
        created_issue = issue_manager.create_issue("Get Test", "Test description")
        
        # Retrieve issue
        retrieved_issue = issue_manager.get_issue(created_issue.id)
        
        assert retrieved_issue is not None
        assert retrieved_issue.id == created_issue.id
        assert retrieved_issue.title == "Get Test"
        assert retrieved_issue.description == "Test description"
    
    def test_get_nonexistent_issue(self, issue_manager):
        """Test retrieving non-existent issue"""
        result = issue_manager.get_issue("nonexistent_id")
        assert result is None
    
    def test_update_issue(self, issue_manager):
        """Test updating an issue"""
        # Create issue
        issue = issue_manager.create_issue("Update Test", "Original description")
        
        # Update issue
        updated_issue = issue_manager.update_issue(
            issue.id,
            description="Updated description",
            status="in_progress",
            labels=["updated", "test"]
        )
        
        assert updated_issue is not None
        assert updated_issue.description == "Updated description"
        assert updated_issue.status == "in_progress"
        assert updated_issue.labels == ["updated", "test"]
        assert updated_issue.updated_at != issue.updated_at
        
        # Verify Git commit was created
        result = issue_manager._run_git_command(["log", "--oneline", "-1"])
        assert "Issue: Update Test" in result.stdout
    
    def test_request_review(self, issue_manager):
        """Test requesting review for an issue"""
        # Create issue
        issue = issue_manager.create_issue("Review Test", "Needs review")
        
        # Request review
        review = issue_manager.request_review(issue.id, "reviewer@example.com")
        
        assert review is not None
        assert review.issue_id == issue.id
        assert review.reviewer == "reviewer@example.com"
        assert review.status == "pending"
        
        # Verify review file exists
        review_file = issue_manager.reviews_dir / f"{review.id}.json"
        assert review_file.exists()
        
        # Verify issue was updated
        updated_issue = issue_manager.get_issue(issue.id)
        assert updated_issue.status == "under_review"
        assert updated_issue.review_status == "pending"
        assert updated_issue.reviewer == "reviewer@example.com"
        
        # Verify Git commits were created
        result = issue_manager._run_git_command(["log", "--oneline", "-2"])
        assert "Review:" in result.stdout
        assert "Issue:" in result.stdout
    
    def test_submit_review_approved(self, issue_manager):
        """Test submitting an approved review"""
        # Create issue and request review
        issue = issue_manager.create_issue("Approval Test", "Test approval")
        review = issue_manager.request_review(issue.id, "reviewer@example.com")
        
        # Submit approved review
        updated_review = issue_manager.submit_review(
            review.id,
            status="approved",
            comments=["Looks good!", "Well implemented"],
            decision_notes="Approved for deployment"
        )
        
        assert updated_review is not None
        assert updated_review.status == "approved"
        assert updated_review.comments == ["Looks good!", "Well implemented"]
        assert updated_review.decision_notes == "Approved for deployment"
        assert updated_review.reviewed_at is not None
        
        # Verify issue was updated
        updated_issue = issue_manager.get_issue(issue.id)
        assert updated_issue.review_status == "approved"
        assert updated_issue.status == "approved"
    
    def test_submit_review_rejected(self, issue_manager):
        """Test submitting a rejected review"""
        # Create issue and request review
        issue = issue_manager.create_issue("Rejection Test", "Test rejection")
        review = issue_manager.request_review(issue.id, "reviewer@example.com")
        
        # Submit rejected review
        updated_review = issue_manager.submit_review(
            review.id,
            status="rejected",
            comments=["Needs more work", "Security concerns"],
            decision_notes="Please address security issues"
        )
        
        assert updated_review.status == "rejected"
        
        # Verify issue was updated
        updated_issue = issue_manager.get_issue(issue.id)
        assert updated_issue.review_status == "rejected"
        assert updated_issue.status == "needs_changes"
    
    def test_submit_review_changes_requested(self, issue_manager):
        """Test submitting a review requesting changes"""
        # Create issue and request review
        issue = issue_manager.create_issue("Changes Test", "Test changes")
        review = issue_manager.request_review(issue.id, "reviewer@example.com")
        
        # Submit review requesting changes
        updated_review = issue_manager.submit_review(
            review.id,
            status="changes_requested",
            comments=["Add unit tests", "Improve error handling"],
            decision_notes="Please add tests before approval"
        )
        
        assert updated_review.status == "changes_requested"
        
        # Verify issue was updated
        updated_issue = issue_manager.get_issue(issue.id)
        assert updated_issue.review_status == "changes_requested"
        assert updated_issue.status == "needs_changes"
    
    def test_list_issues(self, issue_manager):
        """Test listing issues with filters"""
        # Create issues with different statuses
        issue1 = issue_manager.create_issue("Issue 1", "Description 1", assignee="alice@example.com")
        issue2 = issue_manager.create_issue("Issue 2", "Description 2", assignee="bob@example.com")
        issue3 = issue_manager.create_issue("Issue 3", "Description 3", assignee="alice@example.com")
        
        # Update statuses
        issue_manager.update_issue(issue2.id, status="closed")
        issue_manager.update_issue(issue3.id, status="in_progress")
        
        # Test listing all issues
        all_issues = issue_manager.list_issues()
        assert len(all_issues) == 3
        
        # Test filtering by status
        open_issues = issue_manager.list_issues(status="open")
        assert len(open_issues) == 1
        assert open_issues[0].id == issue1.id
        
        closed_issues = issue_manager.list_issues(status="closed")
        assert len(closed_issues) == 1
        assert closed_issues[0].id == issue2.id
        
        # Test filtering by assignee
        alice_issues = issue_manager.list_issues(assignee="alice@example.com")
        assert len(alice_issues) == 2
        
        bob_issues = issue_manager.list_issues(assignee="bob@example.com")
        assert len(bob_issues) == 1
        assert bob_issues[0].id == issue2.id
    
    def test_list_reviews(self, issue_manager):
        """Test listing reviews with filters"""
        # Create issues and reviews
        issue1 = issue_manager.create_issue("Issue 1", "Description 1")
        issue2 = issue_manager.create_issue("Issue 2", "Description 2")
        
        review1 = issue_manager.request_review(issue1.id, "reviewer1@example.com")
        review2 = issue_manager.request_review(issue1.id, "reviewer2@example.com")
        review3 = issue_manager.request_review(issue2.id, "reviewer1@example.com")
        
        # Test listing all reviews
        all_reviews = issue_manager.list_reviews()
        assert len(all_reviews) == 3
        
        # Test filtering by issue
        issue1_reviews = issue_manager.list_reviews(issue_id=issue1.id)
        assert len(issue1_reviews) == 2
        
        issue2_reviews = issue_manager.list_reviews(issue_id=issue2.id)
        assert len(issue2_reviews) == 1
        assert issue2_reviews[0].id == review3.id
        
        # Test filtering by reviewer
        reviewer1_reviews = issue_manager.list_reviews(reviewer="reviewer1@example.com")
        assert len(reviewer1_reviews) == 2
        
        reviewer2_reviews = issue_manager.list_reviews(reviewer="reviewer2@example.com")
        assert len(reviewer2_reviews) == 1
        assert reviewer2_reviews[0].id == review2.id
    
    def test_get_issue_history(self, issue_manager):
        """Test getting Git history for an issue"""
        # Create and update issue multiple times
        issue = issue_manager.create_issue("History Test", "Original description")
        issue_manager.update_issue(issue.id, description="Updated description")
        issue_manager.update_issue(issue.id, status="in_progress")
        
        # Get history
        history = issue_manager.get_issue_history(issue.id)
        
        assert len(history) == 3  # Original + 2 updates
        
        # Verify history entries
        for entry in history:
            assert 'commit_hash' in entry
            assert 'author_name' in entry
            assert 'author_email' in entry
            assert 'date' in entry
            assert 'message' in entry
            assert "History Test" in entry['message']
    
    def test_get_repository_stats(self, issue_manager):
        """Test getting repository statistics"""
        # Create some issues and reviews
        issue1 = issue_manager.create_issue("Stats Test 1", "Description 1")
        issue2 = issue_manager.create_issue("Stats Test 2", "Description 2")
        review1 = issue_manager.request_review(issue1.id, "reviewer@example.com")
        
        # Get stats
        stats = issue_manager.get_repository_stats()
        
        assert 'repository_path' in stats
        assert 'total_commits' in stats
        assert 'total_issues' in stats
        assert 'total_reviews' in stats
        assert 'latest_commit' in stats
        
        assert stats['total_issues'] == 2
        assert stats['total_reviews'] == 1
        assert stats['total_commits'] >= 5  # Initial + 2 issues + 2 updates + 1 review
        
        # Verify latest commit info
        latest = stats['latest_commit']
        assert latest['hash'] is not None
        assert latest['author'] == "Issue Manager"
        assert latest['message'] is not None
    
    def test_complete_workflow(self, issue_manager):
        """Test complete issue workflow from creation to approval"""
        # 1. Create issue
        issue = issue_manager.create_issue(
            title="Complete Workflow Test",
            description="Testing the complete workflow",
            assignee="developer@example.com",
            labels=["feature", "test"]
        )
        
        # 2. Request review
        review = issue_manager.request_review(issue.id, "senior@example.com")
        
        # 3. Submit review
        issue_manager.submit_review(
            review.id,
            status="approved",
            comments=["Excellent work!", "Ready for production"],
            decision_notes="Approved for immediate deployment"
        )
        
        # 4. Verify final state
        final_issue = issue_manager.get_issue(issue.id)
        assert final_issue.status == "approved"
        assert final_issue.review_status == "approved"
        assert final_issue.reviewer == "senior@example.com"
        
        final_review = issue_manager.list_reviews(issue_id=issue.id)[0]
        assert final_review.status == "approved"
        assert final_review.comments == ["Excellent work!", "Ready for production"]
        
        # 5. Verify Git history
        history = issue_manager.get_issue_history(issue.id)
        assert len(history) >= 2  # Create + update after review
        
        # 6. Verify repository stats
        stats = issue_manager.get_repository_stats()
        assert stats['total_issues'] >= 1
        assert stats['total_reviews'] >= 1
        assert stats['total_commits'] >= 4  # Initial + issue + review + updates


def run_tests():
    """Run all tests"""
    print("🧪 Running Real Git Issue Manager Tests")
    print("=" * 50)
    
    # Run pytest
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)