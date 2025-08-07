#!/usr/bin/env python3
"""
Real Git-based Issue Management System
Uses actual Git repositories and operations - no mocks!
"""

import json
import os
import subprocess
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class Issue:
    """Issue entity"""
    id: str
    title: str
    description: str
    status: str = "open"  # open, under_review, approved, rejected, closed
    review_status: str = "not_required"  # not_required, pending, approved, rejected
    assignee: Optional[str] = None
    reviewer: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    labels: List[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
        if self.labels is None:
            self.labels = []


@dataclass
class Review:
    """Review entity"""
    id: str
    issue_id: str
    reviewer: str
    status: str = "pending"  # pending, approved, rejected, changes_requested
    comments: List[str] = None
    decision_notes: Optional[str] = None
    created_at: Optional[str] = None
    reviewed_at: Optional[str] = None
    
    def __post_init__(self):
        if self.comments is None:
            self.comments = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class GitIssueManager:
    """Real Git-based Issue Management System"""
    
    def __init__(self, repo_path: str, author_name: str = "Issue Manager", author_email: str = "issues@yapp.dev"):
        self.repo_path = Path(repo_path)
        self.author_name = author_name
        self.author_email = author_email
        
        # Initialize Git repository
        self._init_repository()
        
        # Set up directory structure
        self.issues_dir = self.repo_path / "issues"
        self.reviews_dir = self.repo_path / "reviews"
        self.metadata_dir = self.repo_path / ".issue_metadata"
        
        self._ensure_directories()
    
    def _init_repository(self):
        """Initialize Git repository"""
        if not self.repo_path.exists():
            self.repo_path.mkdir(parents=True, exist_ok=True)
        
        if not (self.repo_path / ".git").exists():
            # Initialize Git repo
            self._run_git_command(["init"])
            
            # Configure Git user
            self._run_git_command(["config", "user.name", self.author_name])
            self._run_git_command(["config", "user.email", self.author_email])
            
            # Create initial commit
            readme_file = self.repo_path / "README.md"
            readme_file.write_text("# Issue Management Repository\\n\\nThis repository stores issues and reviews as Git objects.\\n")
            
            self._run_git_command(["add", "README.md"])
            self._run_git_command(["commit", "-m", "Initial commit: Issue management repository"])
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        for directory in [self.issues_dir, self.reviews_dir, self.metadata_dir]:
            directory.mkdir(exist_ok=True)
    
    def _run_git_command(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run Git command in repository directory"""
        return subprocess.run(
            ["git"] + args,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=True
        )
    
    def _save_entity(self, entity_type: str, entity_id: str, data: Dict) -> str:
        """Save entity to Git repository"""
        # Determine file path
        if entity_type == "issue":
            file_path = self.issues_dir / f"{entity_id}.json"
        elif entity_type == "review":
            file_path = self.reviews_dir / f"{entity_id}.json"
        else:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        # Write data to file
        file_path.write_text(json.dumps(data, indent=2, default=str))
        
        # Add to Git
        relative_path = file_path.relative_to(self.repo_path)
        self._run_git_command(["add", str(relative_path)])
        
        # Commit to Git
        commit_message = f"{entity_type.title()}: {data.get('title', data.get('id', 'Update'))}"
        result = self._run_git_command(["commit", "-m", commit_message])
        
        # Get commit hash
        commit_hash = self._run_git_command(["rev-parse", "HEAD"]).stdout.strip()
        
        return commit_hash
    
    def _load_entity(self, entity_type: str, entity_id: str) -> Optional[Dict]:
        """Load entity from Git repository"""
        if entity_type == "issue":
            file_path = self.issues_dir / f"{entity_id}.json"
        elif entity_type == "review":
            file_path = self.reviews_dir / f"{entity_id}.json"
        else:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        if not file_path.exists():
            return None
        
        return json.loads(file_path.read_text())
    
    def create_issue(self, title: str, description: str, assignee: str = None, labels: List[str] = None) -> Issue:
        """Create a new issue"""
        issue_id = f"issue_{uuid.uuid4().hex[:8]}"
        
        issue = Issue(
            id=issue_id,
            title=title,
            description=description,
            assignee=assignee,
            labels=labels or []
        )
        
        # Save to Git
        commit_hash = self._save_entity("issue", issue_id, asdict(issue))
        
        print(f"✅ Created issue {issue_id}: {title}")
        print(f"   Commit: {commit_hash[:8]}")
        
        return issue
    
    def get_issue(self, issue_id: str) -> Optional[Issue]:
        """Get issue by ID"""
        data = self._load_entity("issue", issue_id)
        if not data:
            return None
        
        return Issue(**data)
    
    def update_issue(self, issue_id: str, **updates) -> Optional[Issue]:
        """Update an existing issue"""
        issue_data = self._load_entity("issue", issue_id)
        if not issue_data:
            return None
        
        # Apply updates
        issue_data.update(updates)
        issue_data['updated_at'] = datetime.now().isoformat()
        
        # Save to Git
        commit_hash = self._save_entity("issue", issue_id, issue_data)
        
        print(f"✅ Updated issue {issue_id}")
        print(f"   Commit: {commit_hash[:8]}")
        
        return Issue(**issue_data)
    
    def request_review(self, issue_id: str, reviewer: str) -> Optional[Review]:
        """Request review for an issue"""
        # Check if issue exists
        issue = self.get_issue(issue_id)
        if not issue:
            print(f"❌ Issue {issue_id} not found")
            return None
        
        # Update issue status
        self.update_issue(
            issue_id,
            status="under_review",
            review_status="pending",
            reviewer=reviewer
        )
        
        # Create review
        review_id = f"review_{uuid.uuid4().hex[:8]}"
        review = Review(
            id=review_id,
            issue_id=issue_id,
            reviewer=reviewer
        )
        
        # Save review to Git
        commit_hash = self._save_entity("review", review_id, asdict(review))
        
        print(f"✅ Requested review for issue {issue_id}")
        print(f"   Reviewer: {reviewer}")
        print(f"   Review ID: {review_id}")
        print(f"   Commit: {commit_hash[:8]}")
        
        return review
    
    def submit_review(self, review_id: str, status: str, comments: List[str] = None, decision_notes: str = None) -> Optional[Review]:
        """Submit a review decision"""
        # Load review
        review_data = self._load_entity("review", review_id)
        if not review_data:
            print(f"❌ Review {review_id} not found")
            return None
        
        # Update review
        review_data['status'] = status
        review_data['comments'] = comments or []
        review_data['decision_notes'] = decision_notes
        review_data['reviewed_at'] = datetime.now().isoformat()
        
        # Save review to Git
        commit_hash = self._save_entity("review", review_id, review_data)
        
        # Update issue based on review decision
        issue_id = review_data['issue_id']
        if status == "approved":
            self.update_issue(issue_id, review_status="approved", status="approved")
        elif status == "rejected":
            self.update_issue(issue_id, review_status="rejected", status="needs_changes")
        elif status == "changes_requested":
            self.update_issue(issue_id, review_status="changes_requested", status="needs_changes")
        
        print(f"✅ Submitted review {review_id}: {status}")
        print(f"   Issue: {issue_id}")
        print(f"   Commit: {commit_hash[:8]}")
        
        return Review(**review_data)
    
    def list_issues(self, status: str = None, assignee: str = None) -> List[Issue]:
        """List issues with optional filters"""
        issues = []
        
        if not self.issues_dir.exists():
            return issues
        
        for issue_file in self.issues_dir.glob("*.json"):
            try:
                data = json.loads(issue_file.read_text())
                issue = Issue(**data)
                
                # Apply filters
                if status and issue.status != status:
                    continue
                if assignee and issue.assignee != assignee:
                    continue
                
                issues.append(issue)
            except Exception as e:
                print(f"⚠️  Error loading issue {issue_file}: {e}")
        
        return sorted(issues, key=lambda x: x.created_at, reverse=True)
    
    def list_reviews(self, issue_id: str = None, reviewer: str = None) -> List[Review]:
        """List reviews with optional filters"""
        reviews = []
        
        if not self.reviews_dir.exists():
            return reviews
        
        for review_file in self.reviews_dir.glob("*.json"):
            try:
                data = json.loads(review_file.read_text())
                review = Review(**data)
                
                # Apply filters
                if issue_id and review.issue_id != issue_id:
                    continue
                if reviewer and review.reviewer != reviewer:
                    continue
                
                reviews.append(review)
            except Exception as e:
                print(f"⚠️  Error loading review {review_file}: {e}")
        
        return sorted(reviews, key=lambda x: x.created_at, reverse=True)
    
    def get_issue_history(self, issue_id: str) -> List[Dict]:
        """Get Git history for an issue"""
        issue_file = f"issues/{issue_id}.json"
        
        try:
            # Get Git log for the specific file
            result = self._run_git_command([
                "log", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso", "--", issue_file
            ])
            
            history = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 4)
                    if len(parts) == 5:
                        history.append({
                            'commit_hash': parts[0],
                            'author_name': parts[1],
                            'author_email': parts[2],
                            'date': parts[3],
                            'message': parts[4]
                        })
            
            return history
        except subprocess.CalledProcessError:
            return []
    
    def get_repository_stats(self) -> Dict:
        """Get repository statistics"""
        try:
            # Count commits
            commit_count_result = self._run_git_command(["rev-list", "--count", "HEAD"])
            total_commits = int(commit_count_result.stdout.strip())
            
            # Count issues
            issue_count = len(list(self.issues_dir.glob("*.json"))) if self.issues_dir.exists() else 0
            
            # Count reviews
            review_count = len(list(self.reviews_dir.glob("*.json"))) if self.reviews_dir.exists() else 0
            
            # Get latest commit
            latest_commit_result = self._run_git_command(["log", "-1", "--pretty=format:%H|%an|%ad|%s", "--date=iso"])
            latest_commit_parts = latest_commit_result.stdout.strip().split('|', 3)
            
            return {
                'repository_path': str(self.repo_path),
                'total_commits': total_commits,
                'total_issues': issue_count,
                'total_reviews': review_count,
                'latest_commit': {
                    'hash': latest_commit_parts[0] if len(latest_commit_parts) > 0 else None,
                    'author': latest_commit_parts[1] if len(latest_commit_parts) > 1 else None,
                    'date': latest_commit_parts[2] if len(latest_commit_parts) > 2 else None,
                    'message': latest_commit_parts[3] if len(latest_commit_parts) > 3 else None,
                }
            }
        except subprocess.CalledProcessError as e:
            return {
                'repository_path': str(self.repo_path),
                'error': f"Git command failed: {e}"
            }


def demo_issue_management():
    """Demonstrate the real Git-based issue management system"""
    print("🚀 Real Git-Based Issue Management System Demo")
    print("=" * 60)
    
    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "issue_repo"
        
        # Initialize issue manager
        print("📁 Initializing Git repository...")
        issue_manager = GitIssueManager(str(repo_path))
        
        print(f"   Repository: {repo_path}")
        print()
        
        # Create some issues
        print("📝 Creating Issues...")
        issue1 = issue_manager.create_issue(
            title="Implement user authentication",
            description="Add secure login system with JWT tokens",
            assignee="alice@company.com",
            labels=["feature", "security", "high-priority"]
        )
        
        issue2 = issue_manager.create_issue(
            title="Fix database connection timeout",
            description="Database connections are timing out after 30 seconds",
            assignee="bob@company.com",
            labels=["bug", "database", "urgent"]
        )
        
        issue3 = issue_manager.create_issue(
            title="Add API documentation",
            description="Create comprehensive API documentation with examples",
            assignee="carol@company.com",
            labels=["documentation", "api"]
        )
        print()
        
        # Request reviews
        print("👥 Requesting Reviews...")
        review1 = issue_manager.request_review(issue1.id, "senior_dev@company.com")
        review2 = issue_manager.request_review(issue2.id, "db_expert@company.com")
        print()
        
        # Submit review decisions
        print("✅ Submitting Review Decisions...")
        issue_manager.submit_review(
            review1.id,
            status="approved",
            comments=[
                "Implementation looks solid",
                "Good test coverage",
                "Security considerations are well addressed"
            ],
            decision_notes="Approved for deployment to staging"
        )
        
        issue_manager.submit_review(
            review2.id,
            status="changes_requested",
            comments=[
                "Need to add connection pooling",
                "Consider implementing retry logic",
                "Add monitoring for connection health"
            ],
            decision_notes="Please address the connection pooling before approval"
        )
        print()
        
        # Update an issue
        print("📝 Updating Issues...")
        issue_manager.update_issue(
            issue3.id,
            status="in_progress",
            labels=["documentation", "api", "in-progress"]
        )
        print()
        
        # List issues by status
        print("📋 Listing Issues by Status...")
        
        approved_issues = issue_manager.list_issues(status="approved")
        print(f"   Approved Issues: {len(approved_issues)}")
        for issue in approved_issues:
            print(f"     • {issue.title} (assigned to {issue.assignee})")
        
        needs_changes_issues = issue_manager.list_issues(status="needs_changes")
        print(f"   Issues Needing Changes: {len(needs_changes_issues)}")
        for issue in needs_changes_issues:
            print(f"     • {issue.title} (assigned to {issue.assignee})")
        
        in_progress_issues = issue_manager.list_issues(status="in_progress")
        print(f"   In Progress Issues: {len(in_progress_issues)}")
        for issue in in_progress_issues:
            print(f"     • {issue.title} (assigned to {issue.assignee})")
        print()
        
        # Show issue history
        print("📜 Issue History (Git Log)...")
        history = issue_manager.get_issue_history(issue1.id)
        print(f"   History for {issue1.title}:")
        for entry in history:
            print(f"     • {entry['commit_hash'][:8]} - {entry['message']} ({entry['date'][:10]})")
        print()
        
        # Show repository statistics
        print("📊 Repository Statistics...")
        stats = issue_manager.get_repository_stats()
        print(f"   Total Commits: {stats['total_commits']}")
        print(f"   Total Issues: {stats['total_issues']}")
        print(f"   Total Reviews: {stats['total_reviews']}")
        print(f"   Latest Commit: {stats['latest_commit']['hash'][:8]} - {stats['latest_commit']['message']}")
        print()
        
        # Show Git log
        print("🔍 Git Commit Log...")
        try:
            result = issue_manager._run_git_command([
                "log", "--oneline", "--graph", "--decorate", "-10"
            ])
            print("   Recent commits:")
            for line in result.stdout.strip().split('\n'):
                print(f"     {line}")
        except subprocess.CalledProcessError:
            print("   Could not retrieve Git log")
        print()
        
        print("🎉 Demo Complete!")
        print("=" * 60)
        print("✅ Successfully demonstrated:")
        print("   • Real Git repository creation and management")
        print("   • Issue creation, updates, and status tracking")
        print("   • Review workflow with approval/rejection")
        print("   • Git commit history for full audit trail")
        print("   • Repository statistics and reporting")
        print("   • No mocks - all real Git operations!")


if __name__ == "__main__":
    demo_issue_management()