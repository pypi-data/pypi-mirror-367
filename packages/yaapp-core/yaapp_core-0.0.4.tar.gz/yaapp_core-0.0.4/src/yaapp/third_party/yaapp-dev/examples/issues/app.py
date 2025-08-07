#!/usr/bin/env python3
"""
Issues Plugin Example - yaapp

This example demonstrates:
- Complete issue lifecycle management
- Review workflow with approve/reject/request changes
- Comment system and discussion tracking
- Advanced search and filtering
- Bulk operations and automation

Usage:
  python app.py server           # Run as web server
  python app.py list            # List available functions
  python app.py run <func>      # Run specific function
  python app.py --help          # Get help

Example Commands:
  python app.py run create_sample_issue
  python app.py run list_all_issues
  python app.py run demo_review_workflow
  python app.py run get_issue_statistics
"""

import sys
from pathlib import Path

# Add yaapp to path (for examples in development)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from yaapp import Yaapp
from yaapp.plugins.issues import IssuesPlugin
from yaapp.plugins.storage import Storage

# Create application
app = Yaapp()

# Initialize storage backend (using memory for demo)
storage = Storage(backend="memory")

# Initialize issues plugin
issues = IssuesPlugin(storage_backend=storage, auto_id=True)

# Expose the issues plugin
app.expose(issues, name="issues", custom=True)

# Demo functions to showcase the issues plugin

@app.expose
def create_sample_issue(title: str = "Sample Bug Report", 
                       issue_type: str = "bug",
                       priority: str = "high") -> dict:
    """Create a sample issue to demonstrate the system."""
    issue_id = issues.create(
        title=title,
        description=f"This is a sample {issue_type} issue created for demonstration purposes. "
                   f"It shows how the issues plugin handles {issue_type} reports with {priority} priority.",
        reporter="demo.user@example.com",
        issue_type=issue_type,
        priority=priority,
        tags=["demo", issue_type, "example"],
        labels={"component": "demo", "environment": "development"}
    )
    
    # Add a sample comment
    issues.add_comment(
        issue_id=issue_id,
        text="This issue was created as part of the demo. Please review when convenient.",
        author="demo.user@example.com"
    )
    
    return {
        "issue_id": issue_id,
        "title": title,
        "type": issue_type,
        "priority": priority,
        "message": f"Created sample {issue_type} issue with ID: {issue_id}"
    }

@app.expose
def list_all_issues(status: str = None, limit: int = 10) -> dict:
    """List all issues with optional status filter."""
    issues_list = issues.list(status=status, limit=limit)
    
    return {
        "total_issues": len(issues_list),
        "filter_status": status or "all",
        "issues": [
            {
                "id": issue["id"],
                "title": issue["title"],
                "status": issue["status"],
                "priority": issue["priority"],
                "type": issue.get("issue_type", "unknown"),
                "assignee": issue.get("assignee", "unassigned"),
                "created_at": issue["created_at"],
                "review_summary": issue.get("review_summary", {})
            }
            for issue in issues_list
        ]
    }

@app.expose
def demo_review_workflow(issue_id: str = None) -> dict:
    """Demonstrate the complete review workflow."""
    # Create an issue if none provided
    if not issue_id:
        issue_id = issues.create(
            title="Code Review Required",
            description="New feature implementation needs review before deployment.",
            reporter="developer@example.com",
            issue_type="feature",
            priority="medium",
            assignee="developer@example.com"
        )
    
    # Request review
    review_id = issues.request_review(
        issue_id=issue_id,
        reviewer="senior.developer@example.com",
        requested_by="developer@example.com"
    )
    
    # Submit review decision
    issues.submit_review(
        review_id=review_id,
        status="approved",
        reviewer="senior.developer@example.com",
        comments=["Code looks good", "Tests are comprehensive", "Documentation is clear"],
        decision_notes="Approved with minor suggestions for future improvements"
    )
    
    # Get review status
    review_status = issues.get_review_status(issue_id)
    
    # Transition to in_progress after approval
    issues.update(issue_id, status="in_progress")
    
    return {
        "workflow_demo": "completed",
        "issue_id": issue_id,
        "review_id": review_id,
        "review_status": review_status,
        "final_status": "in_progress",
        "message": "Demonstrated complete review workflow: request -> approve -> transition"
    }

@app.expose
def demo_bulk_operations(count: int = 3) -> dict:
    """Demonstrate bulk operations on multiple issues."""
    # Create multiple issues
    issue_ids = []
    for i in range(count):
        issue_id = issues.create(
            title=f"Bulk Operation Test Issue {i+1}",
            description=f"This is test issue #{i+1} for bulk operations demo.",
            reporter="bulk.tester@example.com",
            issue_type="task",
            priority="low",
            tags=["bulk-test", f"batch-{i+1}"]
        )
        issue_ids.append(issue_id)
    
    # Bulk update - assign all to the same person
    update_results = issues.bulk_update(
        issue_ids=issue_ids,
        updates={
            "assignee": "team.lead@example.com",
            "priority": "medium",
            "status": "in_progress"
        }
    )
    
    # Bulk close some issues
    close_results = issues.bulk_close(
        issue_ids=issue_ids[:2],  # Close first 2 issues
        resolution="completed",
        closed_by="team.lead@example.com"
    )
    
    return {
        "bulk_demo": "completed",
        "created_issues": issue_ids,
        "update_results": update_results,
        "close_results": close_results,
        "message": f"Created {count} issues, updated all, closed {len(close_results)}"
    }

@app.expose
def search_issues(query: str = "demo", fields: list = None) -> dict:
    """Search issues by text query."""
    if fields is None:
        fields = ["title", "description"]
    
    results = issues.search(
        query=query,
        fields=fields
    )
    
    return {
        "search_query": query,
        "search_fields": fields,
        "total_results": len(results),
        "results": [
            {
                "id": issue["id"],
                "title": issue["title"],
                "description": issue["description"][:100] + "..." if len(issue["description"]) > 100 else issue["description"],
                "status": issue["status"],
                "priority": issue["priority"]
            }
            for issue in results
        ]
    }

@app.expose
def get_issue_statistics() -> dict:
    """Get comprehensive issue statistics including review metrics."""
    stats = issues.get_statistics()
    
    # Add some computed metrics
    total_issues = stats.get("total", 0)
    total_reviews = stats.get("reviews", {}).get("total", 0)
    
    return {
        "overview": {
            "total_issues": total_issues,
            "total_reviews": total_reviews,
            "reviews_per_issue": round(total_reviews / total_issues, 2) if total_issues > 0 else 0
        },
        "by_status": stats.get("by_status", {}),
        "by_priority": stats.get("by_priority", {}),
        "by_type": stats.get("by_type", {}),
        "by_assignee": stats.get("by_assignee", {}),
        "review_metrics": stats.get("reviews", {}),
        "recent_activity": len(stats.get("recent_activity", []))
    }

@app.expose
def demo_comment_system(issue_id: str = None) -> dict:
    """Demonstrate the comment and discussion system."""
    # Create an issue if none provided
    if not issue_id:
        issue_id = issues.create(
            title="Discussion Thread Demo",
            description="This issue demonstrates the comment and discussion system.",
            reporter="discussion.starter@example.com",
            issue_type="task",
            priority="medium"
        )
    
    # Add various types of comments
    comment_ids = []
    
    # User comment
    comment_ids.append(issues.add_comment(
        issue_id=issue_id,
        text="I think we should approach this problem by first analyzing the requirements.",
        author="analyst@example.com",
        comment_type="user"
    ))
    
    # System comment
    comment_ids.append(issues.add_comment(
        issue_id=issue_id,
        text="Issue automatically assigned based on component ownership.",
        author="system",
        comment_type="system"
    ))
    
    # Another user comment
    comment_ids.append(issues.add_comment(
        issue_id=issue_id,
        text="I agree with the analysis approach. Let me review the existing documentation.",
        author="reviewer@example.com",
        comment_type="user"
    ))
    
    # Get all comments
    all_comments = issues.get_comments(issue_id)
    
    return {
        "demo": "comment_system",
        "issue_id": issue_id,
        "comment_ids": comment_ids,
        "total_comments": len(all_comments),
        "comments": [
            {
                "id": comment["id"],
                "author": comment["author"],
                "text": comment["text"],
                "type": comment["comment_type"],
                "created_at": comment["created_at"]
            }
            for comment in all_comments
        ]
    }

@app.expose
def get_workflow_status(issue_id: str) -> dict:
    """Get comprehensive workflow status for a specific issue."""
    if not issue_id:
        # Find the first available issue
        all_issues = issues.list(limit=1)
        if not all_issues:
            return {"error": "No issues found. Create an issue first."}
        issue_id = all_issues[0]["id"]
    
    workflow_status = issues.get_workflow_status(issue_id)
    
    return {
        "issue_id": issue_id,
        "workflow_status": workflow_status,
        "message": f"Retrieved comprehensive workflow status for issue {issue_id}"
    }

@app.expose
def demo_automation_rules() -> dict:
    """Demonstrate automation rules setup."""
    # Add a sample automation rule
    issues.add_automation_rule({
        "name": "Auto-assign critical bugs",
        "trigger": "issue_created",
        "conditions": [
            "issue_type == 'bug'",
            "priority == 'critical'"
        ],
        "actions": [
            {"type": "assign", "assignee": "on-call-engineer@example.com"},
            {"type": "add_tag", "tag": "needs-immediate-attention"},
            {"type": "comment", "text": "This critical bug has been automatically assigned to the on-call engineer."}
        ]
    })
    
    # Create a critical bug to trigger the rule
    issue_id = issues.create(
        title="Critical System Failure",
        description="The main system is down and users cannot access the application.",
        reporter="monitoring@example.com",
        issue_type="bug",
        priority="critical"
    )
    
    # Get the issue to see automation effects
    updated_issue = issues.get(issue_id)
    comments = issues.get_comments(issue_id)
    
    return {
        "automation_demo": "completed",
        "rule_added": "Auto-assign critical bugs",
        "triggered_issue": issue_id,
        "assignee": updated_issue.get("assignee"),
        "tags": updated_issue.get("labels", []),
        "automation_comments": len([c for c in comments if c["comment_type"] == "system"]),
        "message": "Automation rule created and triggered successfully"
    }

if __name__ == "__main__":
    app.run()