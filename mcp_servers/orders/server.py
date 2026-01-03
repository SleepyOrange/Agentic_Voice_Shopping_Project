#!/usr/bin/env python3
"""Orders MCP Server - Order management via MCP."""

import json
import logging
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from tools import OrderManager

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("orders-server")
order_manager = OrderManager()


@mcp.tool()
def place_order(
    items: list,
    total: float,
    delivery_address: dict,
    contact_email: str
) -> str:
    """
    Place a new order.

    Args:
        items: List of items (each with product_id, name, price, quantity)
        total: Order total in GBP
        delivery_address: Delivery address (name, street, city, postcode, country)
        contact_email: Customer email for confirmation

    Returns:
        Order confirmation with order ID and estimated delivery
    """
    try:
        result = order_manager.place_order(items, total, delivery_address, contact_email)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_order_status(order_id: str) -> str:
    """
    Get the status of an order.

    Args:
        order_id: The order ID to look up (e.g., 'ORD-A1B2C3D4')

    Returns:
        Order status, items, and tracking information if shipped
    """
    try:
        result = order_manager.get_order_status(order_id)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting order status: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_orders_by_email(email: str) -> str:
    """
    Get all orders for an email address.

    Args:
        email: Customer email address

    Returns:
        List of all orders for this email
    """
    try:
        result = order_manager.get_orders_by_email(email)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()
