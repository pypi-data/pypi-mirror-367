"""
Approval state management implementation.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any

from .base import BaseState, StateError, ValidationError


@dataclass
class ApprovalRequest:
    """Approval request entity."""
    id: str
    request_type: str
    title: str
    description: str
    requester: str
    amount: Optional[float] = None
    currency: str = "USD"
    status: str = "pending"
    priority: str = "medium"
    data: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
        if self.data is None:
            self.data = {}


@dataclass
class Approval:
    """Individual approval entity."""
    id: str
    request_id: str
    approver: str
    level: int
    status: str = "pending"
    decision: Optional[str] = None  # approved, rejected
    comments: Optional[str] = None
    approved_at: Optional[str] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class ApprovalState(BaseState):
    """
    Approval state management with multi-level workflow.
    
    Manages approval workflows including:
    - Multi-level approval chains
    - Automatic routing based on rules
    - Parallel and sequential approvals
    - Escalation and delegation
    - Approval policies and thresholds
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        "pending": ["approved", "rejected", "escalated", "cancelled"],
        "escalated": ["approved", "rejected", "cancelled"],
        "approved": ["completed", "cancelled"],
        "rejected": ["resubmitted", "cancelled"],
        "resubmitted": ["pending", "cancelled"],
        "completed": [],  # Terminal state
        "cancelled": []   # Terminal state
    }
    
    VALID_REQUEST_TYPES = ["expense", "purchase", "hire", "contract", "budget", "policy"]
    VALID_PRIORITIES = ["low", "medium", "high", "urgent"]
    
    # Approval rules based on request type and amount
    APPROVAL_RULES = {
        "expense": [
            {"max_amount": 1000, "levels": 1, "approvers": ["manager"]},
            {"max_amount": 5000, "levels": 2, "approvers": ["manager", "director"]},
            {"max_amount": float('inf'), "levels": 3, "approvers": ["manager", "director", "cfo"]}
        ],
        "purchase": [
            {"max_amount": 500, "levels": 1, "approvers": ["supervisor"]},
            {"max_amount": 2000, "levels": 2, "approvers": ["supervisor", "manager"]},
            {"max_amount": 10000, "levels": 3, "approvers": ["supervisor", "manager", "director"]},
            {"max_amount": float('inf'), "levels": 4, "approvers": ["supervisor", "manager", "director", "ceo"]}
        ],
        "hire": [
            {"max_amount": float('inf'), "levels": 3, "approvers": ["hiring_manager", "hr_director", "ceo"]}
        ],
        "contract": [
            {"max_amount": 10000, "levels": 2, "approvers": ["legal", "director"]},
            {"max_amount": float('inf'), "levels": 3, "approvers": ["legal", "director", "ceo"]}
        ]
    }
    
    def __init__(self, storage):
        """Initialize approval state manager."""
        super().__init__(storage, "approval")
        
        # Add validators
        self.add_validator('title', lambda x: len(x.strip()) >= 5, "Title must be at least 5 characters")
        self.add_validator('description', lambda x: len(x.strip()) >= 10, "Description must be at least 10 characters")
        self.add_validator('request_type', lambda x: x in self.VALID_REQUEST_TYPES, f"Request type must be one of {self.VALID_REQUEST_TYPES}")
        self.add_validator('priority', lambda x: x in self.VALID_PRIORITIES, f"Priority must be one of {self.VALID_PRIORITIES}")
        self.add_validator('requester', lambda x: '@' in x, "Requester must be a valid email")
        self.add_validator('amount', lambda x: x is None or x > 0, "Amount must be positive if specified")
    
    def get_valid_transitions(self, current_state: str) -> List[str]:
        """Get valid state transitions from current state."""
        return self.VALID_TRANSITIONS.get(current_state, [])
    
    def create_entity(self, request_type: str, title: str, description: str,
                     requester: str, amount: float = None, currency: str = "USD",
                     priority: str = "medium", data: Dict[str, Any] = None,
                     **kwargs) -> str:
        """Create a new approval request."""
        request_id = self._generate_id("approval")
        
        request_data = {
            "id": request_id,
            "request_type": request_type,
            "title": title.strip(),
            "description": description.strip(),
            "requester": requester,
            "amount": amount,
            "currency": currency,
            "status": "pending",
            "priority": priority,
            "data": data or {},
            "created_by": requester,
            **kwargs
        }
        
        # Validate request data
        errors = self._validate_entity(request_data)
        if errors:
            raise ValidationError(f"Approval request validation failed: {', '.join(errors)}")
        
        # Store request
        success = self._store_entity(request_id, request_data)
        if not success:
            raise StateError(f"Failed to create approval request {request_id}")
        
        # Record initial state
        self._record_state_change(
            request_id, None, "pending", requester, "Approval request created"
        )
        
        # Auto-create required approvals based on rules
        self._create_required_approvals(request_id, request_type, amount or 0)
        
        # Emit creation event
        self._emit('entity_created',
                  entity_id=request_id,
                  entity_type=self.entity_type,
                  entity=request_data)
        
        return request_id
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get approval request by ID."""
        return self._retrieve_entity(entity_id)
    
    def update_entity(self, entity_id: str, **updates) -> bool:
        """Update approval request with validation."""
        request_data = self._retrieve_entity(entity_id)
        if not request_data:
            return False
        
        # Validate status transitions if status is being updated
        if 'status' in updates:
            current_status = request_data.get('status', 'pending')
            new_status = updates['status']
            
            if new_status not in self.get_valid_transitions(current_status):
                raise ValidationError(
                    f"Invalid transition from {current_status} to {new_status}"
                )
        
        # Apply updates
        old_data = request_data.copy()
        request_data.update(updates)
        request_data['updated_at'] = datetime.now().isoformat()
        
        # Validate updated data
        errors = self._validate_entity(request_data)
        if errors:
            raise ValidationError(f"Approval request update validation failed: {', '.join(errors)}")
        
        # Store updated request
        success = self._store_entity(entity_id, request_data)
        
        if success:
            # Emit update event
            self._emit('entity_updated',
                      entity_id=entity_id,
                      entity_type=self.entity_type,
                      old_data=old_data,
                      new_data=request_data,
                      changes=updates)
        
        return success
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete approval request and related approvals."""
        # Delete related approvals
        self._delete_related_approvals(entity_id)
        
        # Delete the request itself
        success = self._delete_entity(entity_id)
        
        if success:
            self._emit('entity_deleted',
                      entity_id=entity_id,
                      entity_type=self.entity_type)
        
        return success
    
    def list_entities(self, requester: str = None, request_type: str = None,
                     status: str = None, priority: str = None,
                     **filters) -> List[Dict[str, Any]]:
        """List approval requests with filters."""
        query_filters = {}
        
        if requester:
            query_filters['requester'] = requester
        if request_type:
            query_filters['request_type'] = request_type
        if status:
            query_filters['status'] = status
        if priority:
            query_filters['priority'] = priority
        
        # Add any additional filters
        query_filters.update(filters)
        
        return self._list_entities(query_filters)
    
    # Approval-specific methods
    
    def create_request(self, request_type: str, title: str, description: str,
                      requester: str, **kwargs) -> str:
        """Create a new approval request (alias for create_entity)."""
        return self.create_entity(request_type, title, description, requester, **kwargs)
    
    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get approval request as ApprovalRequest object."""
        data = self.get_entity(request_id)
        if data:
            return ApprovalRequest(**data)
        return None
    
    def submit_for_approval(self, request_id: str, submitted_by: str = None) -> bool:
        """Submit request for approval (if not already submitted)."""
        request = self.get_entity(request_id)
        if not request:
            return False
        
        if request.get('status') != 'pending':
            raise StateError(f"Request {request_id} is not in pending state")
        
        # Notify approvers
        approvals = self.get_approvals(request_id=request_id)
        pending_approvals = [a for a in approvals if a.status == "pending"]
        
        if pending_approvals:
            # Get first level approvers
            first_level = min(a.level for a in pending_approvals)
            first_level_approvers = [a for a in pending_approvals if a.level == first_level]
            
            for approval in first_level_approvers:
                self._emit('approval_requested',
                          request_id=request_id,
                          approval_id=approval.id,
                          approver=approval.approver,
                          level=approval.level)
        
        return True
    
    def approve_request(self, request_id: str, approver: str, comments: str = None) -> bool:
        """Approve a request at the approver's level."""
        # Find the approval for this approver
        approvals = self.get_approvals(request_id=request_id, approver=approver)
        if not approvals:
            raise StateError(f"No approval found for {approver} on request {request_id}")
        
        approval = approvals[0]  # Should be only one per approver per request
        
        if approval.status != "pending":
            raise StateError(f"Approval {approval.id} is not pending")
        
        # Update approval
        approval_data = self.storage.get(f"approval_item:{approval.id}")
        approval_data.update({
            'status': 'completed',
            'decision': 'approved',
            'comments': comments,
            'approved_at': datetime.now().isoformat()
        })
        
        success = self.storage.set(f"approval_item:{approval.id}", approval_data)
        if not success:
            return False
        
        # Check if all required approvals are complete
        self._check_approval_completion(request_id)
        
        # Emit approval event
        self._emit('approval_given',
                  request_id=request_id,
                  approval_id=approval.id,
                  approver=approver,
                  decision='approved')
        
        return True
    
    def reject_request(self, request_id: str, approver: str, reason: str) -> bool:
        """Reject a request."""
        # Find the approval for this approver
        approvals = self.get_approvals(request_id=request_id, approver=approver)
        if not approvals:
            raise StateError(f"No approval found for {approver} on request {request_id}")
        
        approval = approvals[0]
        
        if approval.status != "pending":
            raise StateError(f"Approval {approval.id} is not pending")
        
        # Update approval
        approval_data = self.storage.get(f"approval_item:{approval.id}")
        approval_data.update({
            'status': 'completed',
            'decision': 'rejected',
            'comments': reason,
            'approved_at': datetime.now().isoformat()
        })
        
        success = self.storage.set(f"approval_item:{approval.id}", approval_data)
        if not success:
            return False
        
        # Reject the entire request
        self.transition_state(request_id, "rejected", approver, f"Rejected: {reason}")
        
        # Emit rejection event
        self._emit('approval_given',
                  request_id=request_id,
                  approval_id=approval.id,
                  approver=approver,
                  decision='rejected')
        
        return True
    
    def escalate_request(self, request_id: str, escalated_by: str, reason: str) -> bool:
        """Escalate a request to higher authority."""
        return self.transition_state(
            request_id, "escalated", escalated_by,
            f"Escalated: {reason}"
        )
    
    def cancel_request(self, request_id: str, cancelled_by: str, reason: str = None) -> bool:
        """Cancel an approval request."""
        return self.transition_state(
            request_id, "cancelled", cancelled_by,
            reason or "Request cancelled"
        )
    
    def resubmit_request(self, request_id: str, resubmitted_by: str,
                        updates: Dict[str, Any] = None) -> bool:
        """Resubmit a rejected request with optional updates."""
        request = self.get_entity(request_id)
        if not request:
            return False
        
        if request.get('status') != 'rejected':
            raise StateError(f"Only rejected requests can be resubmitted")
        
        # Apply updates if provided
        if updates:
            self.update_entity(request_id, **updates)
        
        # Reset all approvals to pending
        approvals = self.get_approvals(request_id=request_id)
        for approval in approvals:
            approval_data = self.storage.get(f"approval_item:{approval.id}")
            approval_data.update({
                'status': 'pending',
                'decision': None,
                'comments': None,
                'approved_at': None
            })
            self.storage.set(f"approval_item:{approval.id}", approval_data)
        
        # Transition back to pending
        return self.transition_state(
            request_id, "pending", resubmitted_by,
            "Request resubmitted"
        )
    
    def get_approvals(self, request_id: str = None, approver: str = None) -> List[Approval]:
        """Get approvals with optional filters."""
        pattern = "approval_item:*"
        approval_keys = self.storage.keys(pattern)
        
        approvals = []
        for key in approval_keys:
            approval_data = self.storage.get(key)
            if approval_data:
                if request_id and approval_data.get('request_id') != request_id:
                    continue
                if approver and approval_data.get('approver') != approver:
                    continue
                approvals.append(Approval(**approval_data))
        
        # Sort by level, then creation time
        return sorted(approvals, key=lambda a: (a.level, a.created_at))
    
    def get_pending_approvals(self, approver: str) -> List[Approval]:
        """Get pending approvals for a specific approver."""
        approvals = self.get_approvals(approver=approver)
        return [a for a in approvals if a.status == "pending"]
    
    def get_approval_status(self, request_id: str) -> Dict[str, Any]:
        """Get comprehensive approval status for request."""
        request = self.get_entity(request_id)
        if not request:
            return {"error": "Request not found"}
        
        approvals = self.get_approvals(request_id=request_id)
        history = self.get_entity_history(request_id)
        
        # Group approvals by level
        approvals_by_level = {}
        for approval in approvals:
            level = approval.level
            if level not in approvals_by_level:
                approvals_by_level[level] = []
            approvals_by_level[level].append(approval)
        
        return {
            "request_id": request_id,
            "status": request.get("status"),
            "request_type": request.get("request_type"),
            "priority": request.get("priority"),
            "amount": request.get("amount"),
            "requester": request.get("requester"),
            "total_approvals": len(approvals),
            "pending_approvals": len([a for a in approvals if a.status == "pending"]),
            "completed_approvals": len([a for a in approvals if a.status == "completed"]),
            "approvals_by_level": {
                str(level): [
                    {
                        "approver": a.approver,
                        "status": a.status,
                        "decision": a.decision,
                        "approved_at": a.approved_at
                    }
                    for a in level_approvals
                ]
                for level, level_approvals in approvals_by_level.items()
            },
            "available_transitions": self.get_valid_transitions(request.get("status")),
            "created_at": request.get("created_at"),
            "last_updated": request.get("updated_at"),
            "state_changes": len(history)
        }
    
    def _create_required_approvals(self, request_id: str, request_type: str, amount: float):
        """Create required approvals based on rules."""
        rules = self.APPROVAL_RULES.get(request_type, [])
        
        # Find applicable rule
        applicable_rule = None
        for rule in rules:
            if amount <= rule["max_amount"]:
                applicable_rule = rule
                break
        
        if not applicable_rule:
            # Default rule - single approval
            applicable_rule = {"levels": 1, "approvers": ["manager"]}
        
        # Create approval items for each level
        for level in range(1, applicable_rule["levels"] + 1):
            approver_role = applicable_rule["approvers"][level - 1] if level <= len(applicable_rule["approvers"]) else "manager"
            
            approval_id = self._generate_id("approval_item")
            approval_data = {
                "id": approval_id,
                "request_id": request_id,
                "approver": approver_role,  # In real system, this would be resolved to actual user
                "level": level,
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
            
            self.storage.set(f"approval_item:{approval_id}", approval_data)
    
    def _check_approval_completion(self, request_id: str):
        """Check if all required approvals are complete."""
        approvals = self.get_approvals(request_id=request_id)
        
        # Check if all approvals are completed with approval
        all_approved = all(
            a.status == "completed" and a.decision == "approved"
            for a in approvals
        )
        
        if all_approved:
            # All approvals complete - approve the request
            self.transition_state(
                request_id, "approved", "system",
                "All required approvals obtained"
            )
        else:
            # Check if we need to notify next level approvers
            completed_levels = set(
                a.level for a in approvals
                if a.status == "completed" and a.decision == "approved"
            )
            
            if completed_levels:
                next_level = max(completed_levels) + 1
                next_level_approvals = [
                    a for a in approvals
                    if a.level == next_level and a.status == "pending"
                ]
                
                for approval in next_level_approvals:
                    self._emit('approval_requested',
                              request_id=request_id,
                              approval_id=approval.id,
                              approver=approval.approver,
                              level=approval.level)
    
    def _delete_related_approvals(self, request_id: str):
        """Delete all approvals related to a request."""
        approvals = self.get_approvals(request_id=request_id)
        for approval in approvals:
            self.storage.delete(f"approval_item:{approval.id}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get approval statistics."""
        stats = super().get_statistics()
        
        # Add approval-specific statistics
        requests = self.list_entities()
        
        # Count by request type
        stats['by_request_type'] = {}
        for request in requests:
            req_type = request.get('request_type', 'unknown')
            stats['by_request_type'][req_type] = stats['by_request_type'].get(req_type, 0) + 1
        
        # Count by priority
        stats['by_priority'] = {}
        for request in requests:
            priority = request.get('priority', 'unknown')
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
        
        # Amount statistics
        amounts = [r.get('amount', 0) for r in requests if r.get('amount')]
        if amounts:
            stats['amounts'] = {
                'total': sum(amounts),
                'average': sum(amounts) / len(amounts),
                'max': max(amounts),
                'min': min(amounts)
            }
        
        # Approval statistics
        all_approvals = self.get_approvals()
        stats['approvals'] = {
            'total': len(all_approvals),
            'pending': len([a for a in all_approvals if a.status == "pending"]),
            'completed': len([a for a in all_approvals if a.status == "completed"]),
            'approved': len([a for a in all_approvals if a.decision == "approved"]),
            'rejected': len([a for a in all_approvals if a.decision == "rejected"])
        }
        
        return stats