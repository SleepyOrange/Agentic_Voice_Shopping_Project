"""Shared data models used across MCP servers."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    """Product model."""
    id: str
    name: str
    description: str
    category: str
    price: float
    image_url: Optional[str] = None
    attributes: list[str] = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = []


@dataclass
class Address:
    """Delivery address model."""
    name: str
    street: str
    city: str
    postcode: str
    country: str = "UK"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "street": self.street,
            "city": self.city,
            "postcode": self.postcode,
            "country": self.country
        }
