"""
Multi-Server Orchestration
============================
Demonstrates connecting a single MCP client to MULTIPLE servers
simultaneously and routing requests across them.

This is how Claude Desktop works — it connects to all configured
servers and presents their combined tools/resources to the AI.

Architecture:
    Client (Orchestrator)
        ├── connects to → Server A (filesystem tools)
        ├── connects to → Server B (database tools)
        └── connects to → Server C (weather tools)

Run:
    python multi_server_client.py
"""

import asyncio
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MultiServerClient:
    """
    Connects to multiple MCP servers and provides a unified interface
    over all their combined tools and resources.
    """

    def __init__(self):
        self._sessions: dict[str, ClientSession] = {}
        # Maps tool_name → server_name for fast routing
        self._tool_registry: dict[str, str] = {}
        self._exit_stack = AsyncExitStack()

    async def connect(self, name: str, command: str, args: list[str]) -> None:
        """Add and connect to an MCP server."""
        params = StdioServerParameters(command=command, args=args)
        read, write = await self._exit_stack.enter_async_context(
            stdio_client(params)
        )
        session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await session.initialize()
        self._sessions[name] = session

        # Register this server's tools
        tools_result = await session.list_tools()
        for tool in tools_result.tools:
            self._tool_registry[tool.name] = name
            print(f"  Registered tool '{tool.name}' from '{name}'")

        print(f"✅ Connected to '{name}' ({len(tools_result.tools)} tools)")

    async def list_all_tools(self) -> dict[str, list[dict]]:
        """List all tools across all connected servers."""
        all_tools = {}
        for server_name, session in self._sessions.items():
            result = await session.list_tools()
            all_tools[server_name] = [
                {"name": t.name, "description": t.description}
                for t in result.tools
            ]
        return all_tools

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Call a tool by name — automatically routes to the correct server.
        """
        server_name = self._tool_registry.get(tool_name)
        if not server_name:
            return {"error": f"Tool '{tool_name}' not found in any connected server."}

        session = self._sessions[server_name]
        result = await session.call_tool(tool_name, arguments)

        if result.content:
            return result.content[0].text if hasattr(result.content[0], "text") else str(result.content[0])
        return None

    async def close(self):
        await self._exit_stack.aclose()


async def demo():
    """
    Demo: Connect to two servers and use tools from both.
    """
    print("=" * 55)
    print("  MULTI-SERVER MCP CLIENT DEMO")
    print("=" * 55)

    client = MultiServerClient()

    try:
        print("\n📡 Connecting to servers...")

        # Connect to filesystem server
        await client.connect(
            "filesystem",
            "python",
            ["../04-intermediate/01-filesystem-server/filesystem_server.py"],
        )

        # Connect to weather server
        await client.connect(
            "weather",
            "python",
            ["../04-intermediate/03-weather-server/weather_server.py"],
        )

        print("\n📦 All available tools:")
        all_tools = await client.list_all_tools()
        for server_name, tools in all_tools.items():
            print(f"\n  [{server_name}]")
            for t in tools:
                print(f"    • {t['name']}: {t['description'][:50]}...")

        print("\n🔧 Calling tools across servers:\n")

        # Call filesystem tool
        result = await client.call_tool("list_dir", {"path": "."})
        print(f"list_dir('.') → {str(result)[:100]}...")

        # Call weather tool
        result = await client.call_tool("get_current_weather", {"city": "Tokyo"})
        print(f"get_current_weather('Tokyo') → {str(result)[:150]}...")

    finally:
        await client.close()
        print("\n👋 Disconnected from all servers.")


if __name__ == "__main__":
    asyncio.run(demo())
