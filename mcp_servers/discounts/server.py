#!/usr/bin/env python3
"""Discounts MCP Server - Discount codes and promotions via MCP."""

import json
import logging
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from tools import DiscountManager

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("discounts-server")
discount_manager = DiscountManager()


@mcp.tool()
def apply_discount(code: str, order_total: float) -> str:
    """
    Apply a discount code to an order.

    Args:
        code: The discount code (e.g., 'CAMP20', 'WELCOME')
        order_total: Current order total in GBP

    Returns:
        Discount details including savings and new total
    """
    try:
        result = discount_manager.apply_discount(code, order_total)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error applying discount: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_promotions() -> str:
    """
    Get all currently active promotions.

    Returns:
        List of active discount codes and their details
    """
    try:
        result = discount_manager.get_promotions()
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting promotions: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def validate_code(code: str) -> str:
    """
    Check if a discount code is valid (without applying it).

    Args:
        code: The discount code to validate

    Returns:
        Whether the code is valid and its details
    """
    try:
        result = discount_manager.validate_code(code)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error validating code: {e}")
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()
