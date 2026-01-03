#!/usr/bin/env python3
"""Products MCP Server - Exposes product catalogue tools via MCP."""

import json
import logging
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from tools import ProductCatalogue

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("products-server")
catalogue = ProductCatalogue()


@mcp.tool()
def search_products(
    query: str,
    category: str = None,
    max_price: float = None,
    limit: int = 5
) -> str:
    """
    Search the product catalogue using natural language.

    Args:
        query: Search terms (e.g., 'lightweight tent', 'warm sleeping bag')
        category: Optional category filter (tents, sleeping_bags, backpacks, etc.)
        max_price: Optional maximum price in GBP
        limit: Maximum number of results (default 5)

    Returns:
        Matching products with name, description, price, and attributes
    """
    try:
        result = catalogue.search_products(
            query=query,
            category=category,
            max_price=max_price,
            limit=limit
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_product(product_id: str) -> str:
    """
    Get detailed information about a specific product.

    Args:
        product_id: The product ID (e.g., 'T100', 'S201')

    Returns:
        Full product details including description, price, and attributes
    """
    try:
        product = catalogue.get_product(product_id)
        if product:
            return json.dumps(product, indent=2)
        return json.dumps({"error": f"Product not found: {product_id}"})
    except Exception as e:
        logger.error(f"Error getting product: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_categories() -> str:
    """
    Get all available product categories.

    Returns:
        List of category names
    """
    try:
        categories = catalogue.get_categories()
        return json.dumps({"categories": categories})
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()
