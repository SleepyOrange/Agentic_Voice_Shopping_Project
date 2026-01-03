#!/usr/bin/env python3
"""
MCP Host - A CLI that connects to MCP servers and uses Claude for intelligent tool routing.

This host can connect to multiple MCP servers and uses Claude to determine
which tools to call based on user queries.
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

# Load environment variables
load_dotenv(Path(__file__).parent / "WeatherAgent" / ".env")


class MCPHost:
    """MCP Host that connects to multiple MCP servers with Claude integration."""

    def __init__(self):
        self.anthropic = Anthropic()
        self.sessions: dict[str, ClientSession] = {}
        self.tools: list[dict] = []
        self.tool_to_server: dict[str, str] = {}
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, name: str, command: str, args: list[str], cwd: str | None = None) -> None:
        """Connect to an MCP server via stdio."""
        print(f"Connecting to MCP server: {name}...")

        # Always pass full environment to ensure subprocess has access to all vars
        server_params = StdioServerParameters(
            command=command,
            args=args,
            cwd=cwd,
            env={**os.environ},
        )

        # Use stdio_client to establish connection
        read, write = await self.exit_stack.enter_async_context(stdio_client(server_params))
        session = await self.exit_stack.enter_async_context(ClientSession(read, write))

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
            print(f"    - {tool.name}: {tool.description or 'No description'}")

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Call a tool on the appropriate MCP server."""
        server_name = self.tool_to_server.get(tool_name)
        if not server_name:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

        # Extract the actual tool name (remove server prefix)
        actual_tool_name = tool_name.split("__", 1)[1]
        session = self.sessions[server_name]

        try:
            result = await session.call_tool(name=actual_tool_name, arguments=arguments)
            # Handle different result types
            if hasattr(result, 'content'):
                # Extract text content from the result
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

    async def chat(self, user_message: str, conversation_history: list[dict]) -> str:
        """Process a user message using Claude and available MCP tools."""
        conversation_history.append({"role": "user", "content": user_message})

        # Call Claude with the tools
        response = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system="""You are a helpful assistant with access to various tools through MCP servers.
Use the available tools to help answer user questions.
When you need weather information, use the weather tools available to you.
Always provide clear, helpful responses based on the tool results.""",
            tools=self.tools,
            messages=conversation_history,
        )

        # Process the response - handle tool calls if present
        while response.stop_reason == "tool_use":
            # Extract tool use blocks
            assistant_content = response.content
            conversation_history.append({"role": "assistant", "content": assistant_content})

            # Process each tool call
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

            # Add tool results to conversation
            conversation_history.append({"role": "user", "content": tool_results})

            # Continue the conversation
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system="""You are a helpful assistant with access to various tools through MCP servers.
Use the available tools to help answer user questions.
When you need weather information, use the weather tools available to you.
Always provide clear, helpful responses based on the tool results.""",
                tools=self.tools,
                messages=conversation_history,
            )

        # Extract the final text response
        final_response = ""
        for block in response.content:
            if hasattr(block, 'text'):
                final_response += block.text

        conversation_history.append({"role": "assistant", "content": response.content})
        return final_response

    async def cleanup(self) -> None:
        """Clean up all MCP server connections."""
        await self.exit_stack.aclose()
        print("Disconnected from all servers.")


async def main():
    """Main entry point for the MCP Host CLI."""
    host = MCPHost()

    try:
        # Connect to the Weather Agent MCP server
        weather_server_path = Path(__file__).parent / "WeatherAgent" / "weather_mcp_server.py"
        await host.connect_to_server(
            name="weather",
            command=sys.executable,  # Use the current Python interpreter
            args=[str(weather_server_path)],
            cwd=str(Path(__file__).parent / "WeatherAgent"),
        )

        print("\n" + "=" * 50)
        print("MCP Host Ready!")
        print(f"Connected servers: {list(host.sessions.keys())}")
        print(f"Available tools: {len(host.tools)}")
        print("=" * 50)
        print("\nType your questions (or 'quit' to exit):\n")

        conversation_history = []

        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("quit", "exit", "q"):
                    print("Goodbye!")
                    break

                response = await host.chat(user_input, conversation_history)
                print(f"\nAssistant: {response}\n")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                break

    finally:
        await host.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
