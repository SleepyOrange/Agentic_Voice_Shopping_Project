#!/usr/bin/env python3
"""SFCC MCP Server - Exposes Salesforce Commerce Cloud tools via Model Context Protocol."""

import json
import logging
from mcp.server.fastmcp import FastMCP

from sfcc_api import SFCCAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("sfcc-commerce")

# Initialize SFCC API client
sfcc_api = SFCCAPI()


@mcp.tool()
def show_product_listing(
    text: str, category_path: str, user_id: str = "cust:00000001"
) -> str:
    """
    Show a Product Listing Page (PLP) to the customer.

    Args:
        text: Message to display in the banner (e.g., "You want boots? Let me show you something...")
        category_path: Category URL path (e.g., '/s/nto/default/shoes-men-hiking')
        user_id: Customer ID (defaults to 'cust:00000001')

    Returns:
        Confirmation of the navigation action
    """
    try:
        result = sfcc_api.show_plp(text, category_path, user_id)
        return json.dumps({"action": "show_plp", "text": text, "url": category_path, **result})
    except Exception as e:
        logger.error(f"Error showing PLP: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def show_product_detail(
    text: str, product_url: str, user_id: str = "cust:00000001"
) -> str:
    """
    Show a Product Detail Page (PDP) to the customer.

    Args:
        text: Message to display in the banner (e.g., "This one you will love...")
        product_url: Product URL path (e.g., "s/nto/default/mens-radical-agile-mid-nto-tech-1050406A8F.html")
        user_id: Customer ID (defaults to 'cust:00000001')

    Returns:
        Confirmation of the navigation action
    """
    try:
        result = sfcc_api.show_pdp(text, product_url, user_id)
        return json.dumps({"action": "show_pdp", "text": text, "url": product_url, **result})
    except Exception as e:
        logger.error(f"Error showing PDP: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def add_to_basket(
    sku: str, quantity: int = 1, user_id: str = "cust:00000001"
) -> str:
    """
    Add a product to the customer's shopping basket.

    Args:
        sku: Product SKU (e.g., '1050406A8FADS')
        quantity: Number of items to add (defaults to 1)
        user_id: Customer ID (defaults to 'cust:00000001')

    Returns:
        Confirmation of the add to basket action
    """
    try:
        result = sfcc_api.add_to_basket(sku, quantity, user_id)
        return json.dumps({"action": "add_to_basket", "sku": sku, "quantity": quantity, **result})
    except Exception as e:
        logger.error(f"Error adding to basket: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def start_checkout(user_id: str = "cust:00000001") -> str:
    """
    Navigate the customer to the checkout page.

    Args:
        user_id: Customer ID (defaults to 'cust:00000001')

    Returns:
        Confirmation of the checkout navigation
    """
    try:
        result = sfcc_api.start_checkout(user_id)
        return json.dumps({"action": "start_checkout", **result})
    except Exception as e:
        logger.error(f"Error starting checkout: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def place_order(
    security_code: str,
    user_id: str = "cust:00000001",
) -> str:
    """
    Submit payment and place the order. Customer details are already on the page.
    After successful order, navigates to the order confirmation page.

    Args:
        security_code: CVV/security code from the customer's card
        user_id: Customer ID (defaults to 'cust:00000001')

    Returns:
        Confirmation of the order placement with navigation to confirmation page
    """
    try:
        result = sfcc_api.submit_payment(
            security_code=security_code,
            user_id=user_id,
        )
        # Navigate to order confirmation page
        confirmation_url = "/s/nto/default/order/confirmation"
        sfcc_api.show_pdp("Your order has been placed!", confirmation_url, user_id)
        return json.dumps({"action": "place_order", "navigate_to": confirmation_url, **result})
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def offer_discount(discount_percent: int, user_id: str = "cust:00000001") -> str:
    """
    Offer a negotiated discount to the customer for their session.

    Args:
        discount_percent: Discount percentage to apply (e.g., 10 for 10% off)
        user_id: Customer ID (defaults to 'cust:00000001')

    Returns:
        Confirmation of the discount application
    """
    try:
        result = sfcc_api.set_discount(discount_percent, user_id)
        return json.dumps({"action": "offer_discount", "discount": f"{discount_percent}%", **result})
    except Exception as e:
        logger.error(f"Error offering discount: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def show_order_history(user_id: str = "cust:00000001") -> str:
    """
    Navigate the customer to their order history page.

    Args:
        user_id: Customer ID (defaults to 'cust:00000001')

    Returns:
        Confirmation of the navigation to order history
    """
    try:
        result = sfcc_api.show_order_history(user_id)
        return json.dumps({"action": "show_order_history", **result})
    except Exception as e:
        logger.error(f"Error showing order history: {e}")
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()
