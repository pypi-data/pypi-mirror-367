"""
State plugin for YAAPP framework.
Provides high-level entity state management and workflow capabilities.
"""

from .base import BaseState, StateError
from .issue import IssueState
from .order import OrderState
from .approval import ApprovalState

__all__ = [
    "BaseState", "StateError",
    "IssueState", "OrderState", "ApprovalState"
]