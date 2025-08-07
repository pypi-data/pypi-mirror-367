"""
Order state management implementation.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal

from .base import BaseState, StateError, ValidationError


@dataclass
class OrderItem:
    """Order item entity."""
    product_id: str
    name: str
    quantity: int
    unit_price: float
    total_price: float = None
    
    def __post_init__(self):
        if self.total_price is None:
            self.total_price = self.quantity * self.unit_price


@dataclass
class Order:
    """Order entity."""
    id: str
    customer_id: str
    items: List[OrderItem]
    status: str = "created"
    total_amount: float = 0.0
    currency: str = "USD"
    payment_method: Optional[str] = None
    shipping_address: Optional[Dict[str, str]] = None
    tracking_number: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()
        
        # Calculate total if not provided
        if self.total_amount == 0.0 and self.items:
            self.total_amount = sum(item.total_price for item in self.items)


@dataclass
class Payment:
    """Payment entity."""
    id: str
    order_id: str
    amount: float
    currency: str
    method: str
    status: str = "pending"
    transaction_id: Optional[str] = None
    processed_at: Optional[str] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class Shipment:
    """Shipment entity."""
    id: str
    order_id: str
    tracking_number: str
    carrier: str
    status: str = "preparing"
    shipped_at: Optional[str] = None
    delivered_at: Optional[str] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class OrderState(BaseState):
    """
    Order state management with payment and shipping workflow.
    
    Manages the complete lifecycle of orders including:
    - Order creation and validation
    - Payment processing
    - Inventory management
    - Shipping and tracking
    - Order fulfillment
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        "created": ["confirmed", "cancelled"],
        "confirmed": ["paid", "cancelled"],
        "paid": ["processing", "refunded", "cancelled"],
        "processing": ["shipped", "cancelled"],
        "shipped": ["delivered", "returned"],
        "delivered": ["completed", "returned"],
        "completed": [],  # Terminal state
        "cancelled": [],  # Terminal state
        "refunded": [],   # Terminal state
        "returned": ["refunded"]
    }
    
    VALID_PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "bank_transfer", "cash"]
    VALID_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD"]
    
    def __init__(self, storage):
        """Initialize order state manager."""
        super().__init__(storage, "order")
        
        # Add validators
        self.add_validator('customer_id', lambda x: len(x.strip()) > 0, "Customer ID is required")
        self.add_validator('items', lambda x: len(x) > 0, "Order must have at least one item")
        self.add_validator('total_amount', lambda x: x > 0, "Total amount must be positive")
        self.add_validator('currency', lambda x: x in self.VALID_CURRENCIES, f"Currency must be one of {self.VALID_CURRENCIES}")
        self.add_validator('payment_method', lambda x: x is None or x in self.VALID_PAYMENT_METHODS, f"Payment method must be one of {self.VALID_PAYMENT_METHODS}")
    
    def get_valid_transitions(self, current_state: str) -> List[str]:
        """Get valid state transitions from current state."""
        return self.VALID_TRANSITIONS.get(current_state, [])
    
    def create_entity(self, customer_id: str, items: List[Dict[str, Any]],
                     currency: str = "USD", shipping_address: Dict[str, str] = None,
                     created_by: str = "", **kwargs) -> str:
        """Create a new order."""
        order_id = self._generate_id("order")
        
        # Convert item dicts to OrderItem objects
        order_items = []
        for item_data in items:
            order_item = OrderItem(**item_data)
            order_items.append(order_item)
        
        # Calculate total
        total_amount = sum(item.total_price for item in order_items)
        
        order_data = {
            "id": order_id,
            "customer_id": customer_id,
            "items": [asdict(item) for item in order_items],
            "status": "created",
            "total_amount": total_amount,
            "currency": currency,
            "shipping_address": shipping_address,
            "created_by": created_by or customer_id,
            **kwargs
        }
        
        # Validate order data
        errors = self._validate_entity(order_data)
        if errors:
            raise ValidationError(f"Order validation failed: {', '.join(errors)}")
        
        # Store order
        success = self._store_entity(order_id, order_data)
        if not success:
            raise StateError(f"Failed to create order {order_id}")
        
        # Record initial state
        self._record_state_change(
            order_id, None, "created", created_by or customer_id, "Order created"
        )
        
        # Emit creation event
        self._emit('entity_created',
                  entity_id=order_id,
                  entity_type=self.entity_type,
                  entity=order_data)
        
        return order_id
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get order by ID."""
        return self._retrieve_entity(entity_id)
    
    def update_entity(self, entity_id: str, **updates) -> bool:
        """Update order with validation."""
        order_data = self._retrieve_entity(entity_id)
        if not order_data:
            return False
        
        # Validate status transitions if status is being updated
        if 'status' in updates:
            current_status = order_data.get('status', 'created')
            new_status = updates['status']
            
            if new_status not in self.get_valid_transitions(current_status):
                raise ValidationError(
                    f"Invalid transition from {current_status} to {new_status}"
                )
        
        # Apply updates
        old_data = order_data.copy()
        order_data.update(updates)
        order_data['updated_at'] = datetime.now().isoformat()
        
        # Validate updated data
        errors = self._validate_entity(order_data)
        if errors:
            raise ValidationError(f"Order update validation failed: {', '.join(errors)}")
        
        # Store updated order
        success = self._store_entity(entity_id, order_data)
        
        if success:
            # Emit update event
            self._emit('entity_updated',
                      entity_id=entity_id,
                      entity_type=self.entity_type,
                      old_data=old_data,
                      new_data=order_data,
                      changes=updates)
        
        return success
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete order and related data."""
        # Delete related payments and shipments
        self._delete_related_payments(entity_id)
        self._delete_related_shipments(entity_id)
        
        # Delete the order itself
        success = self._delete_entity(entity_id)
        
        if success:
            self._emit('entity_deleted',
                      entity_id=entity_id,
                      entity_type=self.entity_type)
        
        return success
    
    def list_entities(self, customer_id: str = None, status: str = None,
                     currency: str = None, **filters) -> List[Dict[str, Any]]:
        """List orders with filters."""
        query_filters = {}
        
        if customer_id:
            query_filters['customer_id'] = customer_id
        if status:
            query_filters['status'] = status
        if currency:
            query_filters['currency'] = currency
        
        # Add any additional filters
        query_filters.update(filters)
        
        return self._list_entities(query_filters)
    
    # Order-specific methods
    
    def create_order(self, customer_id: str, items: List[Dict[str, Any]], **kwargs) -> str:
        """Create a new order (alias for create_entity)."""
        return self.create_entity(customer_id, items, **kwargs)
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order as Order object."""
        data = self.get_entity(order_id)
        if data:
            # Convert items back to OrderItem objects
            items = [OrderItem(**item) for item in data.get('items', [])]
            data['items'] = items
            return Order(**data)
        return None
    
    def confirm_order(self, order_id: str, confirmed_by: str, **kwargs) -> bool:
        """Confirm an order."""
        return self.transition_state(
            order_id, "confirmed", confirmed_by,
            "Order confirmed", **kwargs
        )
    
    def cancel_order(self, order_id: str, cancelled_by: str, reason: str = None) -> bool:
        """Cancel an order."""
        return self.transition_state(
            order_id, "cancelled", cancelled_by,
            reason or "Order cancelled"
        )
    
    def process_payment(self, order_id: str, payment_method: str, processed_by: str,
                       transaction_id: str = None) -> str:
        """Process payment for an order."""
        order = self.get_entity(order_id)
        if not order:
            raise StateError(f"Order {order_id} not found")
        
        if order.get('status') != 'confirmed':
            raise StateError(f"Order {order_id} must be confirmed before payment")
        
        # Create payment entity
        payment_id = self._generate_id("payment")
        payment_data = {
            "id": payment_id,
            "order_id": order_id,
            "amount": order['total_amount'],
            "currency": order['currency'],
            "method": payment_method,
            "status": "completed",  # Simplified - in real world, this would be "processing"
            "transaction_id": transaction_id,
            "processed_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        success = self.storage.set(f"payment:{payment_id}", payment_data)
        if not success:
            raise StateError(f"Failed to create payment {payment_id}")
        
        # Update order status and payment info
        self.update_entity(order_id, payment_method=payment_method)
        self.transition_state(
            order_id, "paid", processed_by,
            f"Payment processed via {payment_method}",
            payment_id=payment_id
        )
        
        return payment_id
    
    def start_processing(self, order_id: str, processed_by: str) -> bool:
        """Start processing an order."""
        return self.transition_state(
            order_id, "processing", processed_by,
            "Order processing started"
        )
    
    def ship_order(self, order_id: str, tracking_number: str, carrier: str,
                  shipped_by: str) -> str:
        """Ship an order."""
        order = self.get_entity(order_id)
        if not order:
            raise StateError(f"Order {order_id} not found")
        
        if order.get('status') != 'processing':
            raise StateError(f"Order {order_id} must be processing before shipping")
        
        # Create shipment entity
        shipment_id = self._generate_id("shipment")
        shipment_data = {
            "id": shipment_id,
            "order_id": order_id,
            "tracking_number": tracking_number,
            "carrier": carrier,
            "status": "shipped",
            "shipped_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        success = self.storage.set(f"shipment:{shipment_id}", shipment_data)
        if not success:
            raise StateError(f"Failed to create shipment {shipment_id}")
        
        # Update order status and tracking info
        self.update_entity(order_id, tracking_number=tracking_number)
        self.transition_state(
            order_id, "shipped", shipped_by,
            f"Order shipped via {carrier}",
            shipment_id=shipment_id,
            tracking_number=tracking_number
        )
        
        return shipment_id
    
    def deliver_order(self, order_id: str, delivered_by: str,
                     delivery_confirmation: str = None) -> bool:
        """Mark order as delivered."""
        # Update shipment status
        shipments = self.get_shipments(order_id=order_id)
        if shipments:
            shipment = shipments[0]  # Assume one shipment per order
            shipment_data = self.storage.get(f"shipment:{shipment.id}")
            if shipment_data:
                shipment_data.update({
                    'status': 'delivered',
                    'delivered_at': datetime.now().isoformat()
                })
                self.storage.set(f"shipment:{shipment.id}", shipment_data)
        
        return self.transition_state(
            order_id, "delivered", delivered_by,
            "Order delivered",
            delivery_confirmation=delivery_confirmation
        )
    
    def complete_order(self, order_id: str, completed_by: str) -> bool:
        """Complete an order."""
        return self.transition_state(
            order_id, "completed", completed_by,
            "Order completed"
        )
    
    def return_order(self, order_id: str, returned_by: str, reason: str = None) -> bool:
        """Return an order."""
        return self.transition_state(
            order_id, "returned", returned_by,
            reason or "Order returned"
        )
    
    def refund_order(self, order_id: str, refunded_by: str, amount: float = None) -> bool:
        """Refund an order."""
        order = self.get_entity(order_id)
        if not order:
            raise StateError(f"Order {order_id} not found")
        
        refund_amount = amount or order['total_amount']
        
        return self.transition_state(
            order_id, "refunded", refunded_by,
            f"Order refunded: {refund_amount} {order['currency']}",
            refund_amount=refund_amount
        )
    
    def get_payments(self, order_id: str = None) -> List[Payment]:
        """Get payments with optional order filter."""
        pattern = "payment:*"
        payment_keys = self.storage.keys(pattern)
        
        payments = []
        for key in payment_keys:
            payment_data = self.storage.get(key)
            if payment_data:
                if order_id and payment_data.get('order_id') != order_id:
                    continue
                payments.append(Payment(**payment_data))
        
        return sorted(payments, key=lambda p: p.created_at, reverse=True)
    
    def get_shipments(self, order_id: str = None) -> List[Shipment]:
        """Get shipments with optional order filter."""
        pattern = "shipment:*"
        shipment_keys = self.storage.keys(pattern)
        
        shipments = []
        for key in shipment_keys:
            shipment_data = self.storage.get(key)
            if shipment_data:
                if order_id and shipment_data.get('order_id') != order_id:
                    continue
                shipments.append(Shipment(**shipment_data))
        
        return sorted(shipments, key=lambda s: s.created_at, reverse=True)
    
    def get_order_summary(self, order_id: str) -> Dict[str, Any]:
        """Get comprehensive order summary."""
        order = self.get_entity(order_id)
        if not order:
            return {"error": "Order not found"}
        
        payments = self.get_payments(order_id=order_id)
        shipments = self.get_shipments(order_id=order_id)
        history = self.get_entity_history(order_id)
        
        return {
            "order_id": order_id,
            "customer_id": order.get("customer_id"),
            "status": order.get("status"),
            "total_amount": order.get("total_amount"),
            "currency": order.get("currency"),
            "item_count": len(order.get("items", [])),
            "payment_method": order.get("payment_method"),
            "tracking_number": order.get("tracking_number"),
            "payments": len(payments),
            "shipments": len(shipments),
            "available_transitions": self.get_valid_transitions(order.get("status")),
            "created_at": order.get("created_at"),
            "last_updated": order.get("updated_at"),
            "state_changes": len(history)
        }
    
    def _delete_related_payments(self, order_id: str):
        """Delete all payments related to an order."""
        payments = self.get_payments(order_id=order_id)
        for payment in payments:
            self.storage.delete(f"payment:{payment.id}")
    
    def _delete_related_shipments(self, order_id: str):
        """Delete all shipments related to an order."""
        shipments = self.get_shipments(order_id=order_id)
        for shipment in shipments:
            self.storage.delete(f"shipment:{shipment.id}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get order statistics."""
        stats = super().get_statistics()
        
        # Add order-specific statistics
        orders = self.list_entities()
        
        # Revenue statistics
        total_revenue = sum(order.get('total_amount', 0) for order in orders)
        completed_orders = [o for o in orders if o.get('status') == 'completed']
        completed_revenue = sum(order.get('total_amount', 0) for order in completed_orders)
        
        stats['revenue'] = {
            'total': total_revenue,
            'completed': completed_revenue,
            'average_order_value': total_revenue / len(orders) if orders else 0
        }
        
        # Count by currency
        stats['by_currency'] = {}
        for order in orders:
            currency = order.get('currency', 'unknown')
            stats['by_currency'][currency] = stats['by_currency'].get(currency, 0) + 1
        
        # Payment method statistics
        stats['by_payment_method'] = {}
        for order in orders:
            method = order.get('payment_method', 'none')
            stats['by_payment_method'][method] = stats['by_payment_method'].get(method, 0) + 1
        
        return stats