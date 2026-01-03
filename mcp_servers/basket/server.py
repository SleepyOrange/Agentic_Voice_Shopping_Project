#!/usr/bin/env python3
"""Basket MCP Server - Shopping basket management via MCP."""

import json
import logging
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from tools import BasketManager

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("basket-server")
basket = BasketManager()


@mcp.tool()
def add_item(product_id: str, name: str, price: float, quantity: int = 1) -> str:
    """
    Add an item to the shopping basket.

    Args:
        product_id: The product ID to add
        name: Product name
        price: Product price in GBP
        quantity: Quantity to add (default 1)

    Returns:
        Updated basket information
    """
    try:
        result = basket.add_item(product_id, name, price, quantity)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error adding item: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def remove_item(product_id: str) -> str:
    """
    Remove an item from the basket.

    Args:
        product_id: The product ID to remove

    Returns:
        Updated basket information
    """
    try:
        result = basket.remove_item(product_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error removing item: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def update_quantity(product_id: str, quantity: int) -> str:
    """
    Update the quantity of an item in the basket.

    Args:
        product_id: The product ID to update
        quantity: New quantity (0 to remove)

    Returns:
        Updated basket information
    """
    try:
        result = basket.update_quantity(product_id, quantity)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error updating quantity: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_basket() -> str:
    """
    Get the current basket contents.

    Returns:
        All items in the basket with totals
    """
    try:
        result = basket.get_basket()
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting basket: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def clear_basket() -> str:
    """
    Clear all items from the basket.

    Returns:
        Confirmation message
    """
    try:
        result = basket.clear()
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error clearing basket: {e}")
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()
