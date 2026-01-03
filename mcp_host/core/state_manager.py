"""Session state management for the shopping agent."""

from dataclasses import dataclass, field
from typing import Any
from datetime import datetime


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


@dataclass
class SessionState:
    """
    Manages all session state for a shopping conversation.

    This includes:
    - Shopping basket
    - Conversation history
    - User context (preferences, location)
    - Current order information
    """

    # Shopping basket
    basket: list[BasketItem] = field(default_factory=list)
    discount_code: str | None = None
    discount_amount: float = 0.0

    # Conversation
    conversation_history: list[dict] = field(default_factory=list)

    # User context
    user_location: str | None = None
    user_preferences: dict[str, Any] = field(default_factory=dict)

    # Order tracking
    current_order_id: str | None = None

    # Session metadata
    session_start: datetime = field(default_factory=datetime.now)

    @property
    def basket_total(self) -> float:
        """Calculate basket total before discount."""
        return sum(item.subtotal for item in self.basket)

    @property
    def basket_total_with_discount(self) -> float:
        """Calculate basket total after discount."""
        return max(0, self.basket_total - self.discount_amount)

    @property
    def basket_item_count(self) -> int:
        """Total number of items in basket."""
        return sum(item.quantity for item in self.basket)

    def add_to_basket(self, product_id: str, name: str, price: float, quantity: int = 1) -> BasketItem:
        """Add an item to the basket or update quantity if exists."""
        for item in self.basket:
            if item.product_id == product_id:
                item.quantity += quantity
                return item

        new_item = BasketItem(product_id=product_id, name=name, price=price, quantity=quantity)
        self.basket.append(new_item)
        return new_item

    def remove_from_basket(self, product_id: str) -> bool:
        """Remove an item from the basket."""
        for i, item in enumerate(self.basket):
            if item.product_id == product_id:
                self.basket.pop(i)
                return True
        return False

    def clear_basket(self) -> None:
        """Clear all items from the basket."""
        self.basket = []
        self.discount_code = None
        self.discount_amount = 0.0

    def apply_discount(self, code: str, amount: float) -> None:
        """Apply a discount to the basket."""
        self.discount_code = code
        self.discount_amount = amount

    def get_basket_summary(self) -> dict:
        """Get a summary of the current basket."""
        return {
            "items": [
                {
                    "product_id": item.product_id,
                    "name": item.name,
                    "price": item.price,
                    "quantity": item.quantity,
                    "subtotal": item.subtotal
                }
                for item in self.basket
            ],
            "item_count": self.basket_item_count,
            "subtotal": self.basket_total,
            "discount_code": self.discount_code,
            "discount_amount": self.discount_amount,
            "total": self.basket_total_with_discount,
            "currency": "GBP"
        }

    def reset(self) -> None:
        """Reset all session state."""
        self.basket = []
        self.discount_code = None
        self.discount_amount = 0.0
        self.conversation_history = []
        self.user_location = None
        self.user_preferences = {}
        self.current_order_id = None
