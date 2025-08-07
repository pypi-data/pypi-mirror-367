"""
Issue state management implementation.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any

from .base import BaseState, StateError, ValidationError


@dataclass
class Issue:
    """Issue entity."""
    id: str
    title: str
    description: str
    status: str = "open"
    priority: str = "medium"
    reporter: str = ""
    assignee: Optional[str] = None
    reviewer: Optional[str] = None
    labels: List[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: str = ""
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


@dataclass
class Review:
    """Review entity."""
    id: str
    issue_id: str
    reviewer: str
    status: str = "pending"
    comments: List[str] = None
    decision_notes: Optional[str] = None
    created_at: Optional[str] = None
    reviewed_at: Optional[str] = None
    
    def __post_init__(self):
        if self.comments is None:
            self.comments = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class Comment:
    """Comment entity."""
    id: str
    issue_id: str
    author: str
    text: str
    comment_type: str = "user"  # user, system, review
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class IssueState(BaseState):
    """
    Issue state management with review workflow.
    
    Manages the complete lifecycle of issues including:
    - Issue creation and updates
    - Review workflow
    - Status transitions
    - Comments and discussions
    - Assignment management
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        "open": ["under_review", "in_progress", "closed"],
        "under_review": ["approved", "needs_changes", "rejected"],
        "approved": ["in_progress", "closed"],
        "needs_changes": ["under_review", "closed"],
        "rejected": ["open", "closed"],
        "in_progress": ["under_review", "completed", "closed"],
        "completed": ["closed"],
        "closed": []  # Terminal state
    }
    
    VALID_PRIORITIES = ["low", "medium", "high", "critical"]
    
    def __init__(self, storage):
        """Initialize issue state manager."""
        super().__init__(storage, "issue")
        
        # Add validators
        self.add_validator('title', lambda x: len(x.strip()) >= 3, "Title must be at least 3 characters")
        self.add_validator('description', lambda x: len(x.strip()) >= 10, "Description must be at least 10 characters")
        self.add_validator('priority', lambda x: x in self.VALID_PRIORITIES, f"Priority must be one of {self.VALID_PRIORITIES}")
        self.add_validator('reporter', lambda x: '@' in x, "Reporter must be a valid email")
        self.add_validator('assignee', lambda x: x is None or '@' in x, "Assignee must be a valid email or None")
    
    def get_valid_transitions(self, current_state: str) -> List[str]:
        """Get valid state transitions from current state."""
        return self.VALID_TRANSITIONS.get(current_state, [])
    
    def create_entity(self, title: str, description: str, reporter: str,
                     priority: str = "medium", assignee: str = None,
                     labels: List[str] = None, **kwargs) -> str:
        """Create a new issue."""
        issue_id = self._generate_id("issue")
        
        issue_data = {
            "id": issue_id,
            "title": title.strip(),
            "description": description.strip(),
            "status": "open",
            "priority": priority,
            "reporter": reporter,
            "assignee": assignee,
            "labels": labels or [],
            "created_by": reporter,
            **kwargs
        }
        
        # Validate issue data
        errors = self._validate_entity(issue_data)
        if errors:
            raise ValidationError(f"Issue validation failed: {', '.join(errors)}")
        
        # Store issue
        success = self._store_entity(issue_id, issue_data)
        if not success:
            raise StateError(f"Failed to create issue {issue_id}")
        
        # Record initial state
        self._record_state_change(
            issue_id, None, "open", reporter, "Issue created"
        )
        
        # Emit creation event
        self._emit('entity_created', 
                  entity_id=issue_id,
                  entity_type=self.entity_type,
                  entity=issue_data)
        
        return issue_id
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get issue by ID."""
        return self._retrieve_entity(entity_id)
    
    def update_entity(self, entity_id: str, **updates) -> bool:
        """Update issue with validation."""
        issue_data = self._retrieve_entity(entity_id)
        if not issue_data:
            return False
        
        # Validate status transitions if status is being updated
        if 'status' in updates:
            current_status = issue_data.get('status', 'open')
            new_status = updates['status']
            
            if new_status not in self.get_valid_transitions(current_status):
                raise ValidationError(
                    f"Invalid transition from {current_status} to {new_status}"
                )
        
        # Apply updates
        old_data = issue_data.copy()
        issue_data.update(updates)
        issue_data['updated_at'] = datetime.now().isoformat()
        
        # Validate updated data
        errors = self._validate_entity(issue_data)
        if errors:
            raise ValidationError(f"Issue update validation failed: {', '.join(errors)}")
        
        # Store updated issue
        success = self._store_entity(entity_id, issue_data)
        
        if success:
            # Emit update event
            self._emit('entity_updated',
                      entity_id=entity_id,
                      entity_type=self.entity_type,
                      old_data=old_data,
                      new_data=issue_data,
                      changes=updates)
        
        return success
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete issue and related data."""
        # Delete related reviews and comments
        self._delete_related_reviews(entity_id)
        self._delete_related_comments(entity_id)
        
        # Delete the issue itself
        success = self._delete_entity(entity_id)
        
        if success:
            self._emit('entity_deleted',
                      entity_id=entity_id,
                      entity_type=self.entity_type)
        
        return success
    
    def list_entities(self, status: str = None, assignee: str = None,
                     priority: str = None, reporter: str = None,
                     labels: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """List issues with filters."""
        query_filters = {}
        
        if status:
            query_filters['status'] = status
        if assignee:
            query_filters['assignee'] = assignee
        if priority:
            query_filters['priority'] = priority
        if reporter:
            query_filters['reporter'] = reporter
        if labels:
            # For simplicity, check if any of the requested labels exist
            # In a real implementation, you might want more sophisticated label filtering
            query_filters['labels'] = {'$contains': labels[0]} if labels else None
        
        # Add any additional filters
        query_filters.update(filters)
        
        return self._list_entities(query_filters)
    
    # Issue-specific methods
    
    def create_issue(self, title: str, description: str, reporter: str, **kwargs) -> str:
        """Create a new issue (alias for create_entity)."""
        return self.create_entity(title, description, reporter, **kwargs)
    
    def get_issue(self, issue_id: str) -> Optional[Issue]:
        """Get issue as Issue object."""
        data = self.get_entity(issue_id)
        if data:
            return Issue(**data)
        return None
    
    def assign_issue(self, issue_id: str, assignee: str, assigned_by: str) -> bool:
        """Assign issue to user."""
        issue = self.get_entity(issue_id)
        if not issue:
            return False
        
        old_assignee = issue.get('assignee')
        success = self.update_entity(issue_id, assignee=assignee)
        
        if success:
            # Add system comment about assignment
            self.add_comment(
                issue_id,
                f"Issue assigned to {assignee}" + (f" (previously {old_assignee})" if old_assignee else ""),
                assigned_by,
                comment_type="system"
            )
            
            # Record state change if needed
            self._record_state_change(
                issue_id, None, None, assigned_by,
                f"Assigned to {assignee}"
            )
        
        return success
    
    def request_review(self, issue_id: str, reviewer: str, requested_by: str) -> str:
        """Request review for an issue."""
        issue = self.get_entity(issue_id)
        if not issue:
            raise StateError(f"Issue {issue_id} not found")
        
        # Update issue status
        self.transition_state(
            issue_id, "under_review", requested_by,
            f"Review requested from {reviewer}",
            reviewer=reviewer
        )
        
        # Create review entity
        review_id = self._generate_id("review")
        review_data = {
            "id": review_id,
            "issue_id": issue_id,
            "reviewer": reviewer,
            "status": "pending",
            "comments": [],
            "created_at": datetime.now().isoformat()
        }
        
        success = self.storage.set(f"review:{review_id}", review_data)
        if not success:
            raise StateError(f"Failed to create review {review_id}")
        
        # Add system comment
        self.add_comment(
            issue_id,
            f"Review requested from {reviewer}",
            requested_by,
            comment_type="system"
        )
        
        return review_id
    
    def submit_review(self, review_id: str, status: str, reviewer: str,
                     comments: List[str] = None, decision_notes: str = None) -> bool:
        """Submit review decision."""
        review_data = self.storage.get(f"review:{review_id}")
        if not review_data:
            return False
        
        if review_data['reviewer'] != reviewer:
            raise ValidationError("Only the assigned reviewer can submit this review")
        
        # Update review
        review_data.update({
            'status': status,
            'comments': comments or [],
            'decision_notes': decision_notes,
            'reviewed_at': datetime.now().isoformat()
        })
        
        success = self.storage.set(f"review:{review_id}", review_data)
        if not success:
            return False
        
        # Update issue based on review decision
        issue_id = review_data['issue_id']
        if status == "approved":
            self.transition_state(issue_id, "approved", reviewer, "Review approved")
        elif status == "rejected":
            self.transition_state(issue_id, "rejected", reviewer, "Review rejected")
        elif status == "changes_requested":
            self.transition_state(issue_id, "needs_changes", reviewer, "Changes requested")
        
        # Add review comment to issue
        review_comment = f"Review {status}"
        if decision_notes:
            review_comment += f": {decision_notes}"
        
        self.add_comment(issue_id, review_comment, reviewer, comment_type="review")
        
        return True
    
    def add_comment(self, issue_id: str, text: str, author: str,
                   comment_type: str = "user") -> str:
        """Add comment to issue."""
        issue = self.get_entity(issue_id)
        if not issue:
            raise StateError(f"Issue {issue_id} not found")
        
        comment_id = self._generate_id("comment")
        comment_data = {
            "id": comment_id,
            "issue_id": issue_id,
            "author": author,
            "text": text,
            "comment_type": comment_type,
            "created_at": datetime.now().isoformat()
        }
        
        success = self.storage.set(f"comment:{comment_id}", comment_data)
        if not success:
            raise StateError(f"Failed to create comment {comment_id}")
        
        # Update issue's updated_at timestamp
        self.update_entity(issue_id, updated_at=datetime.now().isoformat())
        
        # Emit comment event
        self._emit('comment_added',
                  issue_id=issue_id,
                  comment_id=comment_id,
                  author=author,
                  text=text)
        
        return comment_id
    
    def get_comments(self, issue_id: str) -> List[Comment]:
        """Get all comments for an issue."""
        pattern = "comment:*"
        comment_keys = self.storage.keys(pattern)
        
        comments = []
        for key in comment_keys:
            comment_data = self.storage.get(key)
            if comment_data and comment_data.get('issue_id') == issue_id:
                comments.append(Comment(**comment_data))
        
        # Sort by creation time
        return sorted(comments, key=lambda c: c.created_at)
    
    def get_reviews(self, issue_id: str = None, reviewer: str = None) -> List[Review]:
        """Get reviews with optional filters."""
        pattern = "review:*"
        review_keys = self.storage.keys(pattern)
        
        reviews = []
        for key in review_keys:
            review_data = self.storage.get(key)
            if review_data:
                if issue_id and review_data.get('issue_id') != issue_id:
                    continue
                if reviewer and review_data.get('reviewer') != reviewer:
                    continue
                reviews.append(Review(**review_data))
        
        # Sort by creation time
        return sorted(reviews, key=lambda r: r.created_at, reverse=True)
    
    def get_workflow_status(self, issue_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow status for issue."""
        issue = self.get_entity(issue_id)
        if not issue:
            return {"error": "Issue not found"}
        
        reviews = self.get_reviews(issue_id=issue_id)
        comments = self.get_comments(issue_id)
        history = self.get_entity_history(issue_id)
        
        return {
            "issue_id": issue_id,
            "status": issue.get("status"),
            "priority": issue.get("priority"),
            "assignee": issue.get("assignee"),
            "reviewer": issue.get("reviewer"),
            "total_reviews": len(reviews),
            "pending_reviews": len([r for r in reviews if r.status == "pending"]),
            "approved_reviews": len([r for r in reviews if r.status == "approved"]),
            "rejected_reviews": len([r for r in reviews if r.status == "rejected"]),
            "total_comments": len(comments),
            "available_transitions": self.get_valid_transitions(issue.get("status")),
            "last_updated": issue.get("updated_at"),
            "state_changes": len(history)
        }
    
    def _delete_related_reviews(self, issue_id: str):
        """Delete all reviews related to an issue."""
        reviews = self.get_reviews(issue_id=issue_id)
        for review in reviews:
            self.storage.delete(f"review:{review.id}")
    
    def _delete_related_comments(self, issue_id: str):
        """Delete all comments related to an issue."""
        comments = self.get_comments(issue_id)
        for comment in comments:
            self.storage.delete(f"comment:{comment.id}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get issue statistics."""
        stats = super().get_statistics()
        
        # Add issue-specific statistics
        issues = self.list_entities()
        
        # Count by priority
        stats['by_priority'] = {}
        for issue in issues:
            priority = issue.get('priority', 'unknown')
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        
        # Count by assignee
        stats['by_assignee'] = {}
        for issue in issues:
            assignee = issue.get('assignee', 'unassigned')
            stats['by_assignee'][assignee] = stats['by_assignee'].get(assignee, 0) + 1
        
        # Review statistics
        all_reviews = self.get_reviews()
        stats['reviews'] = {
            'total': len(all_reviews),
            'pending': len([r for r in all_reviews if r.status == "pending"]),
            'approved': len([r for r in all_reviews if r.status == "approved"]),
            'rejected': len([r for r in all_reviews if r.status == "rejected"])
        }
        
        return stats