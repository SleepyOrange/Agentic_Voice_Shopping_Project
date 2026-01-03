"""Shopping basket management tools."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BasketItem:
    """An item in the shopping basket."""
    product_id: str
    name: str
    price: float
    quantity: int = 1

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "subtotal": self.subtotal
        }


class BasketManager:
    """
    Manages the shopping basket.

    Note: This is a simple in-memory implementation.
    In production, this would connect to a database or session store.
    """

    def __init__(self):
        self.items: list[BasketItem] = []
        self.discount_code: Optional[str] = None
        self.discount_amount: float = 0.0

    @property
    def subtotal(self) -> float:
        """Calculate basket subtotal before discount."""
        return sum(item.subtotal for item in self.items)

    @property
    def total(self) -> float:
        """Calculate basket total after discount."""
        return max(0, self.subtotal - self.discount_amount)

    @property
    def item_count(self) -> int:
        """Total number of items in basket."""
        return sum(item.quantity for item in self.items)

    def add_item(
        self,
        product_id: str,
        name: str,
        price: float,
        quantity: int = 1
    ) -> dict:
        """Add an item to the basket."""
        # Check if item already in basket
        for item in self.items:
            if item.product_id == product_id:
                item.quantity += quantity
                return {
                    "success": True,
                    "action": "updated",
                    "item": item.to_dict(),
                    "basket_total": self.total,
                    "item_count": self.item_count
                }

        # Add new item
        new_item = BasketItem(
            product_id=product_id,
            name=name,
            price=price,
            quantity=quantity
        )
        self.items.append(new_item)

        return {
            "success": True,
            "action": "added",
            "item": new_item.to_dict(),
            "basket_total": self.total,
            "item_count": self.item_count
        }

    def remove_item(self, product_id: str) -> dict:
        """Remove an item from the basket."""
        for i, item in enumerate(self.items):
            if item.product_id == product_id:
                removed = self.items.pop(i)
                return {
                    "success": True,
                    "removed": removed.to_dict(),
                    "basket_total": self.total,
                    "item_count": self.item_count
                }

        return {
            "success": False,
            "error": f"Item not found: {product_id}"
        }

    def update_quantity(self, product_id: str, quantity: int) -> dict:
        """Update the quantity of an item."""
        if quantity <= 0:
            return self.remove_item(product_id)

        for item in self.items:
            if item.product_id == product_id:
                item.quantity = quantity
                return {
                    "success": True,
                    "item": item.to_dict(),
                    "basket_total": self.total,
                    "item_count": self.item_count
                }

        return {
            "success": False,
            "error": f"Item not found: {product_id}"
        }

    def get_basket(self) -> dict:
        """Get the current basket contents."""
        return {
            "items": [item.to_dict() for item in self.items],
            "item_count": self.item_count,
            "subtotal": self.subtotal,
            "discount_code": self.discount_code,
            "discount_amount": self.discount_amount,
            "total": self.total,
            "currency": "GBP"
        }

    def clear(self) -> dict:
        """Clear the basket."""
        self.items = []
        self.discount_code = None
        self.discount_amount = 0.0
        return {"success": True, "message": "Basket cleared"}

    def apply_discount(self, code: str, amount: float) -> None:
        """Apply a discount to the basket."""
        self.discount_code = code
        self.discount_amount = amount
