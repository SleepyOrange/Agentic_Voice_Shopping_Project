"""Product catalogue tools."""

import json
from pathlib import Path
from typing import Optional


class ProductCatalogue:
    """Product catalogue management."""

    def __init__(self, data_path: Path | str | None = None):
        if data_path is None:
            data_path = Path(__file__).parent / "data" / "products.json"

        with open(data_path, "r") as f:
            data = json.load(f)

        self.catalogue_name = data.get("catalog_name", "Product Catalogue")
        self.currency = data.get("currency", "GBP")
        self.products = data.get("products", [])

    def search_products(
        self,
        query: str,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        limit: int = 5
    ) -> dict:
        """
        Search products using natural language query.

        Args:
            query: Search query (keywords, description)
            category: Optional category filter
            max_price: Optional maximum price filter
            limit: Maximum results to return

        Returns:
            Dict with matching products
        """
        query_lower = query.lower()
        results = []

        for product in self.products:
            # Category filter
            if category and product.get("category") != category:
                continue

            # Price filter
            if max_price and product.get("price", 0) > max_price:
                continue

            # Text matching
            searchable = (
                product.get("name", "").lower() + " " +
                product.get("description", "").lower() + " " +
                " ".join(product.get("attributes", []))
            )

            # Score based on keyword matches
            query_words = query_lower.split()
            matches = sum(1 for word in query_words if word in searchable)

            if matches > 0:
                results.append((matches, product))

        # Sort by relevance and limit
        results.sort(key=lambda x: x[0], reverse=True)
        products = [p for _, p in results[:limit]]

        return {
            "query": query,
            "found": len(products),
            "products": products,
            "currency": self.currency
        }

    def get_product(self, product_id: str) -> Optional[dict]:
        """Get a product by ID."""
        for product in self.products:
            if product.get("id") == product_id:
                return product
        return None

    def get_categories(self) -> list[str]:
        """Get all unique categories."""
        categories = set()
        for product in self.products:
            if cat := product.get("category"):
                categories.add(cat)
        return sorted(categories)
