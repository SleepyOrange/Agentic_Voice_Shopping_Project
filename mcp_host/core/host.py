"""
MCP Host - Core orchestrator for the voice shopping agent.

This module provides the main MCPHost class that:
1. Connects to multiple MCP servers
2. Routes tool calls to appropriate servers
3. Manages conversation with Claude
4. Maintains session state
"""

import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .state_manager import SessionState
from .prompt_builder import PromptBuilder


class MCPHost:
    """
    MCP Host that orchestrates the voice shopping experience.

    Connects Claude to multiple MCP servers and manages:
    - Tool discovery and routing
    - Conversation history
    - Session state (basket, user context)
    """

    def __init__(self, config_dir: Path | None = None):
        load_dotenv()

        self.anthropic = Anthropic()
        self.sessions: dict[str, ClientSession] = {}
        self.tools: list[dict] = []
        self.tool_to_server: dict[str, str] = {}
        self.exit_stack = AsyncExitStack()

        # Session state
        self.state = SessionState()

        # Prompt builder
        config_dir = config_dir or Path(__file__).parent.parent / "config"
        self.prompt_builder = PromptBuilder(config_dir / "system_prompts.json")

        # Load server configs
        with open(config_dir / "mcp_servers.json", "r") as f:
            self.server_configs = json.load(f)["servers"]

    async def connect_to_server(
        self,
        name: str,
        command: str,
        args: list[str],
        cwd: str | None = None
    ) -> None:
        """Connect to an MCP server via stdio."""
        print(f"Connecting to MCP server: {name}...")

        server_params = StdioServerParameters(
            command=command,
            args=args,
            cwd=cwd,
            env={**os.environ},
        )

        read, write = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )

        await session.initialize()
        self.sessions[name] = session

        # Discover tools from this server
        tools_response = await session.list_tools()
        for tool in tools_response.tools:
            tool_def = {
                "name": f"{name}__{tool.name}",
                "description": tool.description or f"Tool: {tool.name}",
                "input_schema": tool.inputSchema,
            }
            self.tools.append(tool_def)
            self.tool_to_server[f"{name}__{tool.name}"] = name

        print(f"  Connected! Found {len(tools_response.tools)} tools:")
        for tool in tools_response.tools:
            print(f"    - {tool.name}")

    async def connect_all_servers(self, project_root: Path) -> None:
        """Connect to all enabled MCP servers from config."""
        for name, config in self.server_configs.items():
            if not config.get("enabled", True):
                continue

            try:
                command = sys.executable if config["command"] == "python" else config["command"]
                args = [str(project_root / arg) for arg in config["args"]]
                cwd = str(project_root / config["cwd"]) if config.get("cwd") else str(project_root)

                await self.connect_to_server(name, command, args, cwd)
            except Exception as e:
                print(f"  Failed to connect to {name}: {e}")

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Call a tool on the appropriate MCP server."""
        server_name = self.tool_to_server.get(tool_name)
        if not server_name:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

        actual_tool_name = tool_name.split("__", 1)[1]
        session = self.sessions[server_name]

        try:
            result = await session.call_tool(name=actual_tool_name, arguments=arguments)
            if hasattr(result, 'content'):
                contents = []
                for content in result.content:
                    if hasattr(content, 'text'):
                        contents.append(content.text)
                    else:
                        contents.append(str(content))
                return "\n".join(contents)
            return str(result)
        except Exception as e:
            return json.dumps({"error": str(e)})

    async def chat(self, user_message: str) -> str:
        """
        Process a user message using Claude and available MCP tools.

        Args:
            user_message: The user's input

        Returns:
            The assistant's response
        """
        self.state.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Build dynamic system prompt with session context
        session_context = {
            "user_location": self.state.user_location,
            "basket_item_count": self.state.basket_item_count,
            "basket_total": self.state.basket_total,
        }
        system_prompt = self.prompt_builder.build_system_prompt(
            session_context=session_context
        )

        # Call Claude
        response = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            tools=self.tools,
            messages=self.state.conversation_history,
        )

        # Process tool calls
        while response.stop_reason == "tool_use":
            assistant_content = response.content
            self.state.conversation_history.append({
                "role": "assistant",
                "content": assistant_content
            })

            tool_results = []
            for block in assistant_content:
                if block.type == "tool_use":
                    print(f"  Calling tool: {block.name}...")
                    result = await self.call_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            self.state.conversation_history.append({
                "role": "user",
                "content": tool_results
            })

            response = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system_prompt,
                tools=self.tools,
                messages=self.state.conversation_history,
            )

        # Extract final response
        final_response = ""
        for block in response.content:
            if hasattr(block, 'text'):
                final_response += block.text

        self.state.conversation_history.append({
            "role": "assistant",
            "content": response.content
        })

        return final_response

    async def cleanup(self) -> None:
        """Clean up all MCP server connections."""
        await self.exit_stack.aclose()
        print("Disconnected from all servers.")

    def reset_session(self) -> None:
        """Reset the session state."""
        self.state.reset()
