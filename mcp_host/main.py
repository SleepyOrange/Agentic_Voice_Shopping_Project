#!/usr/bin/env python3
"""
Voice Shopping Agent - Main Entry Point

This is the main entry point for the voice shopping agent.
It initializes the MCP Host and connects to all configured MCP servers.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_host.core import MCPHost


async def main():
    """Main entry point for the Voice Shopping Agent."""
    project_root = Path(__file__).parent.parent

    host = MCPHost(config_dir=Path(__file__).parent / "config")

    try:
        # Connect to all enabled MCP servers
        await host.connect_all_servers(project_root)

        print("\n" + "=" * 50)
        print("  Voice Shopping Agent Ready!")
        print("=" * 50)
        print(f"Connected servers: {list(host.sessions.keys())}")
        print(f"Available tools: {len(host.tools)}")
        print("=" * 50)
        print("\nHow can I help you find camping gear today?")
        print("Type 'quit' to exit, 'reset' to clear session.\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ("quit", "exit", "q"):
                    print("\nThank you for shopping with us. Goodbye!")
                    break

                if user_input.lower() == "reset":
                    host.reset_session()
                    print("\nSession reset. How can I help you?\n")
                    continue

                response = await host.chat(user_input)
                print(f"\nAssistant: {response}\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except EOFError:
                break

    finally:
        await host.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
