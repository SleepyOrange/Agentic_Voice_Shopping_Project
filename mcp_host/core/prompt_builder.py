"""Dynamic system prompt builder for the shopping agent."""

import json
from pathlib import Path
from typing import Any


class PromptBuilder:
    """
    Builds dynamic system prompts from configuration.

    Assembles the master system prompt from:
    - Base prompt (personality, context)
    - Workflow steps
    - Capability-specific prompts with tool mappings
    - Weather-product matching rules
    - Product catalog
    - Response guidelines
    - Current session context
    """

    def __init__(self, config_path: Path | str | None = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "system_prompts.json"

        with open(config_path, "r") as f:
            self.config = json.load(f)

        # Load product catalog
        catalog_path = Path(__file__).parent.parent.parent / "data" / "product_catalog.json"
        if catalog_path.exists():
            with open(catalog_path, "r") as f:
                self.product_catalog = json.load(f)
        else:
            self.product_catalog = None

    def build_system_prompt(
        self,
        include_capabilities: list[str] | None = None,
        session_context: dict[str, Any] | None = None
    ) -> str:
        """
        Build the complete system prompt.

        Args:
            include_capabilities: List of capability keys to include (None = all)
            session_context: Current session context to inject

        Returns:
            Complete system prompt string
        """
        parts = []

        # Base prompt
        parts.append(self.config["base_system_prompt"])

        # Storefront URL
        if "storefront_base_url" in self.config:
            parts.append(f"\n\nStorefront URL: {self.config['storefront_base_url']}")

        # Workflow steps
        if "workflow" in self.config:
            parts.append("\n\n## Workflow - Follow these steps:\n")
            for step_key, step_desc in self.config["workflow"].items():
                step_num = step_key.replace("step_", "").replace("_", ". ", 1)
                parts.append(f"{step_num}: {step_desc}\n")

        # Capabilities with tool mappings
        parts.append("\n\n## Your Capabilities and Tools:\n")
        capabilities = self.config.get("capabilities", {})
        for key, cap in capabilities.items():
            if include_capabilities is None or key in include_capabilities:
                parts.append(f"\n### {cap['name']}\n")
                parts.append(f"{cap.get('description', '')}\n")

                if "tool" in cap:
                    parts.append(f"**Tool to call:** `{cap['tool']}`\n")

                if "when_to_use" in cap:
                    parts.append("**When to use:**\n")
                    for trigger in cap["when_to_use"]:
                        parts.append(f"  - {trigger}\n")

                if "triggers" in cap:
                    parts.append("**Triggers (proactively use when customer says):**\n")
                    for trigger in cap["triggers"]:
                        parts.append(f"  - {trigger}\n")

                if "available_category_paths" in cap:
                    parts.append("**Available category paths:**\n")
                    for cat_name, cat_path in cap["available_category_paths"].items():
                        parts.append(f"  - {cat_name}: `{cat_path}`\n")

                if "tool_parameters" in cap:
                    parts.append("**Tool parameters:**\n")
                    for param, desc in cap["tool_parameters"].items():
                        parts.append(f"  - `{param}`: {desc}\n")

                if "discount_amount" in cap:
                    parts.append(f"**Discount amount:** {cap['discount_amount']}%\n")

                if "response_flow" in cap:
                    parts.append(f"**Response flow:** {cap['response_flow']}\n")

        # Weather-product matching
        if "weather_product_matching" in self.config:
            parts.append("\n\n## Weather-to-Product Matching Rules:\n")
            weather_rules = self.config["weather_product_matching"]
            parts.append(f"{weather_rules.get('description', '')}\n")
            for condition, rule in weather_rules.items():
                if condition == "description":
                    continue
                if isinstance(rule, dict):
                    recommend = rule.get("recommend", [])
                    if isinstance(recommend, list):
                        recommend = ", ".join(recommend)
                    reason = rule.get("reason", "")
                    formatted_condition = condition.replace("_", " ").title()
                    parts.append(f"- **{formatted_condition}:** Recommend {recommend}. {reason}\n")

        # Product catalog
        if self.product_catalog:
            parts.append("\n\n## Product Catalog:\n")
            parts.append(f"Currency: {self.product_catalog.get('currency_symbol', '£')}\n\n")
            for product in self.product_catalog.get("products", []):
                parts.append(f"**{product['name']}** (ID: {product['id']})\n")
                parts.append(f"  - Price: £{product['price']}\n")
                parts.append(f"  - Description: {product['description']}\n")
                parts.append(f"  - URL: {product['url']}\n\n")

        # Response guidelines
        if "response_guidelines" in self.config:
            parts.append("\n## Response Guidelines:\n")
            for key, value in self.config["response_guidelines"].items():
                formatted_key = key.replace("_", " ").title()
                parts.append(f"- **{formatted_key}:** {value}\n")

        # Conversation guidelines
        if "conversation_guidelines" in self.config:
            parts.append("\n## Conversation Guidelines:\n")
            for key, value in self.config["conversation_guidelines"].items():
                formatted_key = key.replace("_", " ").title()
                parts.append(f"- **{formatted_key}:** {value}\n")

        # Session context
        if session_context:
            parts.append("\n\n## Current Session Context:\n")
            if session_context.get("user_location"):
                parts.append(f"- User's camping destination: {session_context['user_location']}\n")
            else:
                parts.append("- User's location: NOT YET KNOWN - Ask before recommending products!\n")
            if session_context.get("basket_item_count", 0) > 0:
                parts.append(f"- Items in basket: {session_context['basket_item_count']}\n")
                parts.append(f"- Basket total: £{session_context['basket_total']:.2f}\n")
            else:
                parts.append("- Basket: Empty\n")

        return "".join(parts)

    def get_capability_tools(self, capability: str) -> list[str]:
        """Get the tools required for a specific capability."""
        cap = self.config.get("capabilities", {}).get(capability, {})
        return cap.get("tools_required", [])

    def get_all_capabilities(self) -> list[str]:
        """Get list of all capability keys."""
        return list(self.config.get("capabilities", {}).keys())
