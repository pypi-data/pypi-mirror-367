"""
Base state management classes and interfaces.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from dataclasses import dataclass, asdict


class StateError(Exception):
    """Base exception for state management errors."""
    pass


class ValidationError(StateError):
    """Raised when state validation fails."""
    pass


class TransitionError(StateError):
    """Raised when invalid state transition is attempted."""
    pass


@runtime_checkable
class StorageProtocol(Protocol):
    """Protocol that storage backends must implement for state management."""
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value by key."""
        ...
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Store value with optional TTL."""
        ...
    
    def delete(self, key: str) -> bool:
        """Delete value by key."""
        ...
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        ...
    
    def keys(self, pattern: Optional[str] = None) -> List[str]:
        """List keys, optionally matching pattern."""
        ...
    
    def clear(self) -> int:
        """Clear all data, return count of items removed."""
        ...


@dataclass
class StateChange:
    """Represents a state change event."""
    entity_id: str
    entity_type: str
    old_state: Optional[str]
    new_state: str
    changed_by: str
    changed_at: str
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Entity:
    """Base entity class."""
    id: str
    entity_type: str
    created_at: str
    updated_at: str
    created_by: str
    status: str = "active"
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create entity from dictionary."""
        return cls(**data)


class BaseState(ABC):
    """
    Base class for all state management implementations.
    
    Provides common functionality for entity lifecycle management,
    state transitions, validation, and audit trails.
    """
    
    def __init__(self, storage: StorageProtocol, entity_type: str = None):
        """
        Initialize state manager.
        
        Args:
            storage: Storage backend implementing StorageProtocol
            entity_type: Type of entities this state manager handles
        """
        self.storage = storage
        self.entity_type = entity_type or self.__class__.__name__.lower().replace('state', '')
        self._event_handlers: Dict[str, List[callable]] = {}
        self._validators: Dict[str, List[tuple]] = {}
    
    def _generate_id(self, prefix: str = None) -> str:
        """Generate unique ID for entities."""
        prefix = prefix or self.entity_type
        return f"{prefix}_{uuid.uuid4().hex[:8]}"
    
    def _get_entity_key(self, entity_id: str) -> str:
        """Get storage key for entity."""
        return f"{self.entity_type}:{entity_id}"
    
    def _get_history_key(self, entity_id: str) -> str:
        """Get storage key for entity history."""
        return f"{self.entity_type}:history:{entity_id}"
    
    def _store_entity(self, entity_id: str, data: Dict[str, Any], 
                     ttl_seconds: Optional[int] = None) -> bool:
        """Store entity with automatic metadata."""
        entity_data = {
            **data,
            'entity_id': entity_id,
            'entity_type': self.entity_type,
            'updated_at': datetime.now().isoformat()
        }
        
        # Ensure created_at is set
        if 'created_at' not in entity_data:
            entity_data['created_at'] = entity_data['updated_at']
        
        return self.storage.set(
            self._get_entity_key(entity_id),
            entity_data,
            ttl_seconds
        )
    
    def _retrieve_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve entity by ID."""
        return self.storage.get(self._get_entity_key(entity_id))
    
    def _delete_entity(self, entity_id: str) -> bool:
        """Delete entity by ID."""
        # Also delete history
        self.storage.delete(self._get_history_key(entity_id))
        return self.storage.delete(self._get_entity_key(entity_id))
    
    def _list_entities(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List entities with optional filters."""
        # Get all keys for this entity type
        pattern = f"{self.entity_type}:*"
        keys = self.storage.keys(pattern)
        
        # Filter out history keys
        entity_keys = [key for key in keys if not key.endswith(':history')]
        
        entities = []
        for key in entity_keys:
            entity = self.storage.get(key)
            if entity and self._matches_filters(entity, filters or {}):
                entities.append(entity)
        
        # Sort by creation date (newest first)
        return sorted(entities, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def _matches_filters(self, entity: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if entity matches filter criteria."""
        for key, value in filters.items():
            if '.' in key:
                # Handle nested keys like 'metadata.category'
                keys = key.split('.')
                entity_value = entity
                for k in keys:
                    if isinstance(entity_value, dict) and k in entity_value:
                        entity_value = entity_value[k]
                    else:
                        entity_value = None
                        break
            else:
                entity_value = entity.get(key)
            
            # Handle different filter types
            if isinstance(value, dict):
                # Handle operators like {'$in': [...], '$gt': 5}
                if not self._apply_filter_operators(entity_value, value):
                    return False
            else:
                # Direct equality
                if entity_value != value:
                    return False
        
        return True
    
    def _apply_filter_operators(self, entity_value: Any, filter_ops: Dict[str, Any]) -> bool:
        """Apply filter operators to entity value."""
        for op, op_value in filter_ops.items():
            if op == '$eq':
                if entity_value != op_value:
                    return False
            elif op == '$ne':
                if entity_value == op_value:
                    return False
            elif op == '$in':
                if entity_value not in op_value:
                    return False
            elif op == '$nin':
                if entity_value in op_value:
                    return False
            elif op == '$gt':
                if not (entity_value is not None and entity_value > op_value):
                    return False
            elif op == '$gte':
                if not (entity_value is not None and entity_value >= op_value):
                    return False
            elif op == '$lt':
                if not (entity_value is not None and entity_value < op_value):
                    return False
            elif op == '$lte':
                if not (entity_value is not None and entity_value <= op_value):
                    return False
            elif op == '$contains':
                if not (entity_value is not None and op_value in str(entity_value)):
                    return False
            elif op == '$regex':
                import re
                if not (entity_value is not None and re.search(op_value, str(entity_value))):
                    return False
        
        return True
    
    def _record_state_change(self, entity_id: str, old_state: Optional[str], 
                           new_state: str, changed_by: str, reason: str = None,
                           metadata: Dict[str, Any] = None) -> bool:
        """Record state change in history."""
        change = StateChange(
            entity_id=entity_id,
            entity_type=self.entity_type,
            old_state=old_state,
            new_state=new_state,
            changed_by=changed_by,
            changed_at=datetime.now().isoformat(),
            reason=reason,
            metadata=metadata
        )
        
        # Get existing history
        history_key = self._get_history_key(entity_id)
        history = self.storage.get(history_key) or []
        
        # Add new change
        history.append(asdict(change))
        
        # Store updated history
        return self.storage.set(history_key, history)
    
    def get_entity_history(self, entity_id: str) -> List[StateChange]:
        """Get state change history for entity."""
        history_key = self._get_history_key(entity_id)
        history_data = self.storage.get(history_key) or []
        
        return [StateChange(**change) for change in history_data]
    
    # Event system
    def on(self, event: str, handler: callable):
        """Register event handler."""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    def _emit(self, event: str, **kwargs):
        """Emit event to registered handlers."""
        for handler in self._event_handlers.get(event, []):
            try:
                handler(**kwargs)
            except Exception as e:
                # Log error but don't break the flow
                print(f"Event handler error for {event}: {e}")
    
    # Validation system
    def add_validator(self, field: str, validator: callable, message: str):
        """Add field validator."""
        if field not in self._validators:
            self._validators[field] = []
        self._validators[field].append((validator, message))
    
    def _validate_entity(self, data: Dict[str, Any]) -> List[str]:
        """Validate entity data."""
        errors = []
        
        for field, validators in self._validators.items():
            if field in data:
                for validator, message in validators:
                    try:
                        if not validator(data[field]):
                            errors.append(f"{field}: {message}")
                    except Exception as e:
                        errors.append(f"{field}: Validation error - {e}")
        
        return errors
    
    # Abstract methods that subclasses must implement
    @abstractmethod
    def get_valid_transitions(self, current_state: str) -> List[str]:
        """Get valid state transitions from current state."""
        pass
    
    @abstractmethod
    def create_entity(self, **kwargs) -> str:
        """Create a new entity."""
        pass
    
    @abstractmethod
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def update_entity(self, entity_id: str, **updates) -> bool:
        """Update entity."""
        pass
    
    @abstractmethod
    def delete_entity(self, entity_id: str) -> bool:
        """Delete entity."""
        pass
    
    @abstractmethod
    def list_entities(self, **filters) -> List[Dict[str, Any]]:
        """List entities with filters."""
        pass
    
    # Optional methods with default implementations
    def get_entity_status(self, entity_id: str) -> Optional[str]:
        """Get current status of entity."""
        entity = self.get_entity(entity_id)
        return entity.get('status') if entity else None
    
    def transition_state(self, entity_id: str, new_state: str, changed_by: str,
                        reason: str = None, **kwargs) -> bool:
        """Transition entity to new state with validation."""
        entity = self.get_entity(entity_id)
        if not entity:
            raise StateError(f"Entity {entity_id} not found")
        
        current_state = entity.get('status')
        valid_transitions = self.get_valid_transitions(current_state)
        
        if new_state not in valid_transitions:
            raise TransitionError(
                f"Invalid transition from {current_state} to {new_state}. "
                f"Valid transitions: {valid_transitions}"
            )
        
        # Record state change
        self._record_state_change(
            entity_id, current_state, new_state, changed_by, reason, kwargs
        )
        
        # Update entity
        success = self.update_entity(entity_id, status=new_state, **kwargs)
        
        if success:
            # Emit state change event
            self._emit('state_changed', 
                      entity_id=entity_id,
                      entity_type=self.entity_type,
                      old_state=current_state,
                      new_state=new_state,
                      changed_by=changed_by,
                      entity=self.get_entity(entity_id))
        
        return success
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics for this entity type."""
        entities = self.list_entities()
        
        stats = {
            'total': len(entities),
            'by_status': {},
            'recent_activity': entities[:10]  # Last 10 entities
        }
        
        # Count by status
        for entity in entities:
            status = entity.get('status', 'unknown')
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        
        return stats
    
    def cleanup_expired(self) -> int:
        """Clean up expired entities if storage supports it."""
        if hasattr(self.storage, 'cleanup_expired'):
            return self.storage.cleanup_expired()
        return 0