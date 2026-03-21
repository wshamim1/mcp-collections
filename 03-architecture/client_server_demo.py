"""
MCP Client-Server Demo — Full Interaction Example
==================================================
Shows a complete MCP client connecting to a server, discovering
capabilities, and exercising tools, resources, and prompts.

This is the "big picture" demo of how all pieces fit together.

Run:
    python client_server_demo.py
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def demo_full_interaction():
    """Demonstrates complete MCP client-server interaction."""

    server_params = StdioServerParameters(
        command="python",
        args=["../02-core-concepts/02-resources/resources_basic.py"],
    )

    print("=" * 60)
    print("  MCP CLIENT-SERVER INTERACTION DEMO")
    print("=" * 60)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # ── Phase 1: Initialize ───────────────────────────────────────────
            server_info = await session.initialize()
            print(f"\n✅ Connected to: {server_info.serverInfo.name}")
            print(f"   MCP version:  {server_info.protocolVersion}")
            print(f"   Capabilities: {list(server_info.capabilities.__dict__.keys())}")

            # ── Phase 2: Discover Tools ───────────────────────────────────────
            print("\n📦 TOOLS DISCOVERY")
            print("-" * 40)
            tools_result = await session.list_tools()
            for tool in tools_result.tools:
                params = list(tool.inputSchema.get("properties", {}).keys())
                print(f"  🔧 {tool.name}({', '.join(params)})")
                print(f"     {tool.description[:70]}...")

            # ── Phase 3: Discover Resources ───────────────────────────────────
            print("\n📂 RESOURCES DISCOVERY")
            print("-" * 40)
            try:
                resources_result = await session.list_resources()
                for resource in resources_result.resources:
                    print(f"  📄 {resource.uri}")
                    if resource.description:
                        print(f"     {resource.description[:60]}...")
            except Exception:
                print("  (no resources or not supported)")

            # ── Phase 4: Discover Prompts ─────────────────────────────────────
            print("\n💬 PROMPTS DISCOVERY")
            print("-" * 40)
            try:
                prompts_result = await session.list_prompts()
                for prompt in prompts_result.prompts:
                    args = [a.name for a in (prompt.arguments or [])]
                    print(f"  💬 {prompt.name}({', '.join(args)})")
            except Exception:
                print("  (no prompts or not supported)")

            print("\n" + "=" * 60)
            print("  CALLING TOOLS")
            print("=" * 60)

            # ── Phase 5: Call Tools ────────────────────────────────────────────
            if tools_result.tools:
                for tool in tools_result.tools[:3]:
                    print(f"\n🔧 Calling: {tool.name}")

            print("\n✅ Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo_full_interaction())
