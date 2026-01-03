"""Discount and promotions tools."""

from datetime import datetime
from dataclasses import dataclass


@dataclass
class Discount:
    """A discount code."""
    code: str
    description: str
    discount_type: str  # 'percentage' or 'fixed'
    value: float
    expires: str
    min_order: float = 0.0

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "description": self.description,
            "type": self.discount_type,
            "value": self.value,
            "expires": self.expires,
            "min_order": self.min_order
        }


class DiscountManager:
    """
    Manages discount codes and promotions.

    Note: This is a simple in-memory implementation.
    In production, this would connect to a database.
    """

    def __init__(self):
        # Pre-configured discount codes
        self.discounts = {
            "CAMP20": Discount(
                code="CAMP20",
                description="20% off your entire order",
                discount_type="percentage",
                value=20,
                expires="2025-12-31"
            ),
            "WELCOME": Discount(
                code="WELCOME",
                description="15% off for new customers",
                discount_type="percentage",
                value=15,
                expires="2025-12-31"
            ),
            "SAVE10": Discount(
                code="SAVE10",
                description="£10 off orders over £50",
                discount_type="fixed",
                value=10,
                expires="2025-12-31",
                min_order=50
            ),
            "WINTER25": Discount(
                code="WINTER25",
                description="25% off winter camping gear",
                discount_type="percentage",
                value=25,
                expires="2025-03-31"
            )
        }

    def apply_discount(self, code: str, order_total: float) -> dict:
        """
        Apply a discount code to an order.

        Args:
            code: The discount code
            order_total: Current order total

        Returns:
            Discount details and new total
        """
        code_upper = code.upper()
        discount = self.discounts.get(code_upper)

        if not discount:
            return {
                "valid": False,
                "code": code,
                "error": "Invalid discount code"
            }

        # Check expiry
        if datetime.strptime(discount.expires, "%Y-%m-%d") < datetime.now():
            return {
                "valid": False,
                "code": code,
                "error": "This discount code has expired"
            }

        # Check minimum order
        if order_total < discount.min_order:
            return {
                "valid": False,
                "code": code,
                "error": f"Minimum order of £{discount.min_order:.2f} required for this code"
            }

        # Calculate discount
        if discount.discount_type == "percentage":
            savings = order_total * (discount.value / 100)
        else:
            savings = discount.value

        savings = min(savings, order_total)  # Can't save more than order total

        return {
            "valid": True,
            "code": discount.code,
            "description": discount.description,
            "discount_type": discount.discount_type,
            "discount_value": discount.value,
            "savings": round(savings, 2),
            "original_total": round(order_total, 2),
            "new_total": round(order_total - savings, 2)
        }

    def get_promotions(self) -> dict:
        """Get all currently active promotions."""
        now = datetime.now()
        active_promos = []

        for discount in self.discounts.values():
            if datetime.strptime(discount.expires, "%Y-%m-%d") >= now:
                active_promos.append(discount.to_dict())

        return {
            "promotions": active_promos,
            "count": len(active_promos)
        }

    def validate_code(self, code: str) -> dict:
        """Check if a code is valid without applying it."""
        code_upper = code.upper()
        discount = self.discounts.get(code_upper)

        if not discount:
            return {"valid": False, "error": "Invalid code"}

        if datetime.strptime(discount.expires, "%Y-%m-%d") < datetime.now():
            return {"valid": False, "error": "Code expired"}

        return {
            "valid": True,
            "discount": discount.to_dict()
        }
