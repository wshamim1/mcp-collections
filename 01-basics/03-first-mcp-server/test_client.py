"""
Test Client for the First MCP Server
=====================================
This script shows how to connect to a local MCP server programmatically
and call its tools — useful for automated testing and understanding the protocol.

Run:
    python test_client.py
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # ─── Connect to the MCP server via stdio ─────────────────────────────────
    server_params = StdioServerParameters(
        command="python",
        args=["simple_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Initialize the connection
            await session.initialize()
            print("✅ Connected to MCP server\n")

            # ─── List available tools ─────────────────────────────────────────
            tools = await session.list_tools()
            print("📦 Available Tools:")
            for tool in tools.tools:
                print(f"  • {tool.name}: {tool.description}")
            print()

            # ─── Call each tool ───────────────────────────────────────────────
            print("🔧 Testing Tools:\n")

            # Test greet
            result = await session.call_tool("greet", {"name": "Alice"})
            print(f"greet('Alice')     → {result.content[0].text}")

            # Test add_numbers
            result = await session.call_tool("add_numbers", {"a": 42, "b": 8})
            print(f"add_numbers(42, 8) → {result.content[0].text}")

            # Test get_current_time
            result = await session.call_tool("get_current_time", {"timezone": "UTC"})
            print(f"get_current_time() → {result.content[0].text}")

            # Test reverse_string
            result = await session.call_tool("reverse_string", {"text": "Hello MCP!"})
            print(f"reverse_string()   → {result.content[0].text}")

            # Test count_words
            result = await session.call_tool("count_words", {"text": "The quick brown fox jumps"})
            print(f"count_words()      → {result.content[0].text}")

            print("\n✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
