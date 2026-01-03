"""Order management tools."""

import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class OrderItem:
    """An item in an order."""
    product_id: str
    name: str
    price: float
    quantity: int

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "subtotal": self.price * self.quantity
        }


@dataclass
class Order:
    """A customer order."""
    order_id: str
    items: list[OrderItem]
    total: float
    status: str
    delivery_address: dict
    contact_email: str
    created_at: datetime = field(default_factory=datetime.now)
    tracking_number: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "items": [item.to_dict() for item in self.items],
            "total": self.total,
            "status": self.status,
            "delivery_address": self.delivery_address,
            "contact_email": self.contact_email,
            "created_at": self.created_at.isoformat(),
            "tracking_number": self.tracking_number,
            "estimated_delivery": (self.created_at + timedelta(days=5)).strftime("%Y-%m-%d")
        }


class OrderManager:
    """
    Manages customer orders.

    Note: This is a simple in-memory implementation.
    In production, this would connect to a database.
    """

    def __init__(self):
        self.orders: dict[str, Order] = {}

    def place_order(
        self,
        items: list[dict],
        total: float,
        delivery_address: dict,
        contact_email: str
    ) -> dict:
        """Place a new order."""
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        order_items = [
            OrderItem(
                product_id=item["product_id"],
                name=item["name"],
                price=item["price"],
                quantity=item["quantity"]
            )
            for item in items
        ]

        order = Order(
            order_id=order_id,
            items=order_items,
            total=total,
            status="confirmed",
            delivery_address=delivery_address,
            contact_email=contact_email
        )

        self.orders[order_id] = order

        return {
            "success": True,
            "order_id": order_id,
            "status": "confirmed",
            "total": total,
            "estimated_delivery": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "confirmation_sent_to": contact_email
        }

    def get_order_status(self, order_id: str) -> dict:
        """Get the status of an order."""
        order = self.orders.get(order_id)

        if not order:
            return {
                "success": False,
                "error": f"Order not found: {order_id}"
            }

        return {
            "success": True,
            "order": order.to_dict()
        }

    def get_orders_by_email(self, email: str) -> dict:
        """Get all orders for an email address."""
        matching_orders = [
            order.to_dict()
            for order in self.orders.values()
            if order.contact_email.lower() == email.lower()
        ]

        return {
            "success": True,
            "email": email,
            "order_count": len(matching_orders),
            "orders": matching_orders
        }

    def update_order_status(self, order_id: str, status: str) -> dict:
        """Update the status of an order."""
        order = self.orders.get(order_id)

        if not order:
            return {
                "success": False,
                "error": f"Order not found: {order_id}"
            }

        order.status = status

        # Add tracking for shipped orders
        if status == "shipped" and not order.tracking_number:
            order.tracking_number = f"TRK{uuid.uuid4().hex[:10].upper()}"

        return {
            "success": True,
            "order_id": order_id,
            "status": status,
            "tracking_number": order.tracking_number
        }
