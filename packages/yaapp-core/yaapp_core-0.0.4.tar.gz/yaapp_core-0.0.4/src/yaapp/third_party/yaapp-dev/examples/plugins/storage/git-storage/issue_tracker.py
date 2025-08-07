#!/usr/bin/env python3
"""
Git Storage Issue Tracker Example

Demonstrates building a complete issue tracking system using Git storage:
- Issue lifecycle management
- Review workflow
- Status transitions
- Audit trails for compliance
- Team collaboration features
"""

import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import YAAPP storage
from yaapp.plugins.storage import create_git_storage_manager


class IssueTracker:
    """Issue tracking system built on Git storage."""
    
    def __init__(self, storage):
        self.storage = storage
    
    def create_issue(self, title: str, description: str, reporter: str, 
                    assignee: str = None, priority: str = "medium", 
                    labels: List[str] = None) -> str:
        """Create a new issue."""
        issue_id = f"issue_{uuid.uuid4().hex[:8]}"
        
        issue_data = {
            "id": issue_id,
            "title": title,
            "description": description,
            "status": "open",
            "priority": priority,
            "reporter": reporter,
            "assignee": assignee,
            "labels": labels or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "comments": [],
            "status_history": [
                {
                    "status": "open",
                    "changed_by": reporter,
                    "changed_at": datetime.now().isoformat(),
                    "reason": "Issue created"
                }
            ]
        }
        
        success = self.storage.set(issue_id, issue_data)
        return issue_id if success else None
    
    def get_issue(self, issue_id: str) -> Optional[Dict]:
        """Get issue by ID."""
        return self.storage.get(issue_id)
    
    def update_issue_status(self, issue_id: str, new_status: str, 
                           changed_by: str, reason: str = None) -> bool:
        """Update issue status with audit trail."""
        issue = self.storage.get(issue_id)
        if not issue:
            return False
        
        old_status = issue["status"]
        issue["status"] = new_status
        issue["updated_at"] = datetime.now().isoformat()
        
        # Add to status history
        issue["status_history"].append({
            "status": new_status,
            "previous_status": old_status,
            "changed_by": changed_by,
            "changed_at": datetime.now().isoformat(),
            "reason": reason or f"Status changed from {old_status} to {new_status}"
        })
        
        return self.storage.set(issue_id, issue)
    
    def add_comment(self, issue_id: str, comment: str, author: str) -> bool:
        """Add comment to issue."""
        issue = self.storage.get(issue_id)
        if not issue:
            return False
        
        comment_data = {
            "id": f"comment_{uuid.uuid4().hex[:8]}",
            "text": comment,
            "author": author,
            "created_at": datetime.now().isoformat()
        }
        
        issue["comments"].append(comment_data)
        issue["updated_at"] = datetime.now().isoformat()
        
        return self.storage.set(issue_id, issue)
    
    def assign_issue(self, issue_id: str, assignee: str, assigned_by: str) -> bool:
        """Assign issue to user."""
        issue = self.storage.get(issue_id)
        if not issue:
            return False
        
        old_assignee = issue.get("assignee")
        issue["assignee"] = assignee
        issue["updated_at"] = datetime.now().isoformat()
        
        # Add comment about assignment
        assignment_comment = {
            "id": f"comment_{uuid.uuid4().hex[:8]}",
            "text": f"Issue assigned to {assignee}" + (f" (previously {old_assignee})" if old_assignee else ""),
            "author": assigned_by,
            "created_at": datetime.now().isoformat(),
            "type": "system"
        }
        
        issue["comments"].append(assignment_comment)
        
        return self.storage.set(issue_id, issue)
    
    def list_issues(self, status: str = None, assignee: str = None) -> List[Dict]:
        """List issues with optional filters."""
        # Get all issue keys
        issue_keys = [key for key in self.storage.keys() if key.startswith("issue_")]
        
        issues = []
        for key in issue_keys:
            issue = self.storage.get(key)
            if issue:
                # Apply filters
                if status and issue.get("status") != status:
                    continue
                if assignee and issue.get("assignee") != assignee:
                    continue
                
                issues.append(issue)
        
        # Sort by creation date (newest first)
        return sorted(issues, key=lambda x: x.get("created_at", ""), reverse=True)
    
    def get_issue_statistics(self) -> Dict:
        """Get issue statistics."""
        all_issues = self.list_issues()
        
        stats = {
            "total": len(all_issues),
            "by_status": {},
            "by_priority": {},
            "by_assignee": {},
            "recent_activity": []
        }
        
        for issue in all_issues:
            # Count by status
            status = issue.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Count by priority
            priority = issue.get("priority", "unknown")
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
            
            # Count by assignee
            assignee = issue.get("assignee", "unassigned")
            stats["by_assignee"][assignee] = stats["by_assignee"].get(assignee, 0) + 1
        
        # Get recent activity (last 5 issues)
        stats["recent_activity"] = all_issues[:5]
        
        return stats


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_subsection(title: str):
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")


def main():
    print_section("Git Storage Issue Tracker Demo")
    
    # Create temporary directory for this demo
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "issue_tracker"
        
        print(f"📁 Repository: {repo_path}")
        
        # Create Git storage manager
        storage = create_git_storage_manager(
            repo_path=str(repo_path),
            author_name="Issue Tracker",
            author_email="issues@company.com"
        )
        
        # Create issue tracker
        tracker = IssueTracker(storage)
        
        print_subsection("Creating Issues")
        
        # Create various issues
        issue1 = tracker.create_issue(
            title="Login page not responsive on mobile",
            description="The login form doesn't display correctly on mobile devices. Buttons are cut off and input fields are too small.",
            reporter="alice@company.com",
            assignee="bob@company.com",
            priority="high",
            labels=["bug", "ui", "mobile"]
        )
        print(f"✅ Created issue: {issue1}")
        
        time.sleep(1)  # Small delay for different timestamps
        
        issue2 = tracker.create_issue(
            title="Add dark mode support",
            description="Users have requested a dark mode option for better usability in low-light conditions.",
            reporter="carol@company.com",
            assignee="alice@company.com",
            priority="medium",
            labels=["feature", "ui", "enhancement"]
        )
        print(f"✅ Created issue: {issue2}")
        
        time.sleep(1)
        
        issue3 = tracker.create_issue(
            title="Database connection timeout",
            description="Application occasionally times out when connecting to the database during peak hours.",
            reporter="bob@company.com",
            priority="critical",
            labels=["bug", "database", "performance"]
        )
        print(f"✅ Created issue: {issue3}")
        
        print_subsection("Issue Management Workflow")
        
        # Add comments
        print("💬 Adding comments...")
        tracker.add_comment(issue1, "I can reproduce this on iPhone 12. The submit button is completely hidden.", "dave@company.com")
        tracker.add_comment(issue1, "Working on a fix. Will have it ready by tomorrow.", "bob@company.com")
        
        tracker.add_comment(issue2, "This would be a great addition! I'd suggest using CSS custom properties for easy theming.", "alice@company.com")
        
        # Assign unassigned issue
        print("👤 Assigning issues...")
        tracker.assign_issue(issue3, "eve@company.com", "alice@company.com")
        
        # Update issue statuses
        print("📝 Updating issue statuses...")
        tracker.update_issue_status(issue1, "in_progress", "bob@company.com", "Started working on mobile responsiveness fix")
        time.sleep(1)
        
        tracker.update_issue_status(issue2, "in_progress", "alice@company.com", "Beginning dark mode implementation")
        time.sleep(1)
        
        tracker.update_issue_status(issue1, "resolved", "bob@company.com", "Fixed mobile layout issues. Ready for testing.")
        time.sleep(1)
        
        tracker.update_issue_status(issue3, "in_progress", "eve@company.com", "Investigating database connection pooling")
        
        print_subsection("Issue Listing and Filtering")
        
        # List all issues
        all_issues = tracker.list_issues()
        print(f"📋 Total issues: {len(all_issues)}")
        
        for issue in all_issues:
            status_icon = {"open": "🔓", "in_progress": "⚡", "resolved": "✅", "closed": "🔒"}.get(issue["status"], "❓")
            priority_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(issue["priority"], "⚪")
            
            print(f"  {status_icon} {priority_icon} {issue['id']}: {issue['title']}")
            print(f"    Status: {issue['status']} | Priority: {issue['priority']} | Assignee: {issue.get('assignee', 'Unassigned')}")
            print(f"    Labels: {', '.join(issue['labels'])}")
            print()
        
        # Filter by status
        print("🔍 Filtering by status:")
        in_progress_issues = tracker.list_issues(status="in_progress")
        print(f"  In Progress: {len(in_progress_issues)} issues")
        for issue in in_progress_issues:
            print(f"    • {issue['title']} (assigned to {issue.get('assignee', 'Unassigned')})")
        
        # Filter by assignee
        print(f"\n👤 Issues assigned to alice@company.com:")
        alice_issues = tracker.list_issues(assignee="alice@company.com")
        for issue in alice_issues:
            print(f"    • {issue['title']} ({issue['status']})")
        
        print_subsection("Detailed Issue View")
        
        # Show detailed view of an issue
        detailed_issue = tracker.get_issue(issue1)
        if detailed_issue:
            print(f"📄 Issue Details: {detailed_issue['id']}")
            print(f"   Title: {detailed_issue['title']}")
            print(f"   Description: {detailed_issue['description']}")
            print(f"   Status: {detailed_issue['status']}")
            print(f"   Priority: {detailed_issue['priority']}")
            print(f"   Reporter: {detailed_issue['reporter']}")
            print(f"   Assignee: {detailed_issue.get('assignee', 'Unassigned')}")
            print(f"   Labels: {', '.join(detailed_issue['labels'])}")
            print(f"   Created: {detailed_issue['created_at']}")
            print(f"   Updated: {detailed_issue['updated_at']}")
            
            print(f"\n   📝 Comments ({len(detailed_issue['comments'])}):")
            for comment in detailed_issue['comments']:
                comment_type = f" [{comment['type']}]" if comment.get('type') else ""
                print(f"     • {comment['author']}{comment_type}: {comment['text']}")
                print(f"       {comment['created_at']}")
            
            print(f"\n   📊 Status History:")
            for status_change in detailed_issue['status_history']:
                print(f"     • {status_change['status']} by {status_change['changed_by']}")
                print(f"       {status_change['changed_at']} - {status_change['reason']}")
        
        print_subsection("Issue Statistics")
        
        # Get and display statistics
        stats = tracker.get_issue_statistics()
        
        print(f"📊 Issue Statistics:")
        print(f"   Total Issues: {stats['total']}")
        
        print(f"\n   By Status:")
        for status, count in stats['by_status'].items():
            print(f"     {status}: {count}")
        
        print(f"\n   By Priority:")
        for priority, count in stats['by_priority'].items():
            print(f"     {priority}: {count}")
        
        print(f"\n   By Assignee:")
        for assignee, count in stats['by_assignee'].items():
            print(f"     {assignee}: {count}")
        
        print_subsection("Audit Trail and History")
        
        # Show Git audit trail
        git_backend = storage.get_backend("default")
        if hasattr(git_backend, 'get_history'):
            print("📜 Git Audit Trail:")
            
            # Get history for one of the issues
            history = git_backend.get_history(issue1)
            print(f"\n   History for {issue1} ({len(history)} changes):")
            
            for i, entry in enumerate(history[:5], 1):  # Show last 5 changes
                print(f"     {i}. {entry['commit_hash'][:8]} - {entry['message']}")
                print(f"        {entry['date']} by {entry['author_name']}")
        
        print_subsection("Repository Statistics")
        
        # Show repository statistics
        if hasattr(git_backend, 'get_repository_stats'):
            repo_stats = git_backend.get_repository_stats()
            
            print("📈 Repository Statistics:")
            print(f"   Total Commits: {repo_stats.get('total_commits')}")
            print(f"   Total Keys: {repo_stats.get('total_keys')}")
            print(f"   Repository Size: {repo_stats.get('repository_size_bytes')} bytes")
            print(f"   Cache Size: {repo_stats.get('cache_size')} items")
            
            latest = repo_stats.get('latest_commit', {})
            if latest:
                print(f"   Latest Commit: {latest.get('hash', '')[:8]} - {latest.get('message', '')}")
        
        print_section("Issue Tracker Demo Complete")
        
        print("🎉 Features Demonstrated:")
        print("   • Complete issue lifecycle management")
        print("   • Status transitions with audit trails")
        print("   • Comment system with authorship")
        print("   • Assignment and reassignment")
        print("   • Filtering and search capabilities")
        print("   • Comprehensive statistics")
        print("   • Git-based audit trail")
        print("   • Immutable change history")
        print("   • Team collaboration features")
        
        print("\n💡 Benefits of Git Storage:")
        print("   • Every change is tracked and immutable")
        print("   • Complete audit trail for compliance")
        print("   • Distributed collaboration support")
        print("   • Backup and recovery built-in")
        print("   • Cryptographic data integrity")
        print("   • No data loss - everything is versioned")


if __name__ == "__main__":
    main()