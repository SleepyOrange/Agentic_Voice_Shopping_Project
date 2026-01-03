"""Dynamic system prompt builder for the shopping agent."""

import json
from pathlib import Path
from typing import Any


class PromptBuilder:
    """
    Builds dynamic system prompts from configuration.

    Assembles the master system prompt from:
    - Base prompt (personality, context)
    - Capability-specific prompts
    - Voice considerations
    - Current session context
    """

    def __init__(self, config_path: Path | str | None = None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "system_prompts.json"

        with open(config_path, "r") as f:
            self.config = json.load(f)

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

        # Capabilities
        parts.append("\n\n## Your Capabilities:\n")

        capabilities = self.config.get("capabilities", {})
        for key, cap in capabilities.items():
            if include_capabilities is None or key in include_capabilities:
                parts.append(f"\n### {cap['name']}\n{cap['system_prompt']}\n")

        # Voice considerations
        if "voice_considerations" in self.config:
            parts.append("\n\n## Voice Interaction Guidelines:\n")
            for key, value in self.config["voice_considerations"].items():
                formatted_key = key.replace("_", " ").title()
                parts.append(f"- **{formatted_key}**: {value}\n")

        # Session context
        if session_context:
            parts.append("\n\n## Current Session Context:\n")
            if session_context.get("user_location"):
                parts.append(f"- User's location: {session_context['user_location']}\n")
            if session_context.get("basket_item_count", 0) > 0:
                parts.append(f"- Items in basket: {session_context['basket_item_count']}\n")
                parts.append(f"- Basket total: £{session_context['basket_total']:.2f}\n")

        return "".join(parts)

    def get_capability_tools(self, capability: str) -> list[str]:
        """Get the tools required for a specific capability."""
        cap = self.config.get("capabilities", {}).get(capability, {})
        return cap.get("tools_required", [])

    def get_all_capabilities(self) -> list[str]:
        """Get list of all capability keys."""
        return list(self.config.get("capabilities", {}).keys())
