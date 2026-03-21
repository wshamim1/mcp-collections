"""
Claude + MCP Integration
=========================
Shows how to use Anthropic's Claude API with MCP tools.
Claude natively supports MCP-style tool use through its API.

This example:
1. Starts an MCP server as a subprocess
2. Discovers its tools
3. Passes tools to Claude
4. Handles Claude's tool calls → routes to MCP server
5. Returns final response

Requirements:
    pip install anthropic mcp

Set your API key:
    export ANTHROPIC_API_KEY=your-key-here

Run:
    python claude_with_mcp.py
"""

import asyncio
import json
import os
from typing import Any

import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ─── Configuration ──────────────────────────────────────────────────────────
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
MAX_TOKENS = 4096


# ─── MCP ↔ Claude Tool Conversion ─────────────────────────────────────────────

def mcp_tool_to_claude_format(mcp_tool) -> dict:
    """
    Convert an MCP tool definition to Claude's tool format.

    MCP format:  { name, description, inputSchema }
    Claude format: { name, description, input_schema }
    """
    return {
        "name": mcp_tool.name,
        "description": mcp_tool.description or f"Tool: {mcp_tool.name}",
        "input_schema": mcp_tool.inputSchema,
    }


# ─── Main Agent Loop ──────────────────────────────────────────────────────────

async def run_claude_with_mcp(user_message: str, server_script: str) -> str:
    """
    Run Claude with tools from an MCP server.

    Args:
        user_message: The user's question or request.
        server_script: Path to the MCP server Python script.

    Returns:
        Claude's final response text.
    """
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    server_params = StdioServerParameters(
        command="python",
        args=[server_script],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Get all tools from the MCP server
            tools_result = await session.list_tools()
            claude_tools = [mcp_tool_to_claude_format(t) for t in tools_result.tools]

            print(f"🔧 Loaded {len(claude_tools)} tools from MCP server")
            print(f"💬 User: {user_message}\n")

            # Agentic loop: keep going until Claude stops calling tools
            messages = [{"role": "user", "content": user_message}]

            while True:
                response = client.messages.create(
                    model=CLAUDE_MODEL,
                    max_tokens=MAX_TOKENS,
                    tools=claude_tools,
                    messages=messages,
                )

                # Check why Claude stopped
                if response.stop_reason == "end_turn":
                    # Claude is done — extract final text
                    final_text = " ".join(
                        block.text
                        for block in response.content
                        if hasattr(block, "text")
                    )
                    return final_text

                elif response.stop_reason == "tool_use":
                    # Claude wants to use tools
                    # Add Claude's response to message history
                    messages.append({"role": "assistant", "content": response.content})

                    # Process each tool call
                    tool_results = []
                    for block in response.content:
                        if block.type != "tool_use":
                            continue

                        print(f"  🔧 Claude calls: {block.name}({json.dumps(block.input)[:80]}...)")

                        # Route the call to MCP server
                        mcp_result = await session.call_tool(block.name, block.input)

                        # Extract text content from result
                        result_content = ""
                        for content_block in mcp_result.content:
                            if hasattr(content_block, "text"):
                                result_content += content_block.text

                        print(f"  📤 Result: {result_content[:100]}...")

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_content,
                        })

                    # Feed tool results back to Claude
                    messages.append({"role": "user", "content": tool_results})

                else:
                    # Unexpected stop reason
                    return f"Unexpected stop reason: {response.stop_reason}"


# ─── Demo ──────────────────────────────────────────────────────────────────

async def main():
    print("=" * 55)
    print("  CLAUDE + MCP INTEGRATION DEMO")
    print("=" * 55)

    # Demo questions to ask Claude
    questions = [
        "What's the weather like in Tokyo and London today? Compare them.",
        "List the files in the current directory and tell me what kind of project this is.",
    ]

    for question in questions:
        print(f"\n{'─' * 55}")
        response = await run_claude_with_mcp(
            user_message=question,
            # Use the weather server for weather questions
            server_script="../../04-intermediate/03-weather-server/weather_server.py",
        )
        print(f"\n🤖 Claude: {response}")


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌  Please set ANTHROPIC_API_KEY environment variable")
        print("    export ANTHROPIC_API_KEY=your-key-here")
        exit(1)

    asyncio.run(main())
