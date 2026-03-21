"""
OpenAI GPT + MCP Integration
==============================
Shows how to connect OpenAI's GPT models to MCP servers.
OpenAI uses "function calling" which maps directly to MCP tools.

Requirements:
    pip install openai mcp

Set your API key:
    export OPENAI_API_KEY=your-key-here

Run:
    python openai_with_mcp.py
"""

import asyncio
import json
import os
from typing import Any

import openai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ─── Configuration ──────────────────────────────────────────────────────────
GPT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")


# ─── MCP ↔ OpenAI Tool Conversion ─────────────────────────────────────────────

def mcp_tool_to_openai_format(mcp_tool) -> dict:
    """
    Convert MCP tool to OpenAI function-calling format.

    MCP:    { name, description, inputSchema }
    OpenAI: { type: "function", function: { name, description, parameters } }
    """
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description or f"Tool: {mcp_tool.name}",
            "parameters": mcp_tool.inputSchema,
        },
    }


# ─── Agent Loop ───────────────────────────────────────────────────────────────

async def run_gpt_with_mcp(
    user_message: str,
    server_script: str,
    system_prompt: str = "You are a helpful assistant with access to various tools.",
) -> str:
    """
    Run GPT with tools from an MCP server.

    Args:
        user_message: The user's question.
        server_script: Path to the MCP server script.
        system_prompt: System message for GPT.

    Returns:
        GPT's final response.
    """
    oai_client = openai.AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

    server_params = StdioServerParameters(command="python", args=[server_script])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            openai_tools = [mcp_tool_to_openai_format(t) for t in tools_result.tools]

            print(f"🔧 Loaded {len(openai_tools)} tools")
            print(f"💬 User: {user_message}\n")

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ]

            # Agentic loop
            while True:
                response = await oai_client.chat.completions.create(
                    model=GPT_MODEL,
                    messages=messages,
                    tools=openai_tools if openai_tools else openai.NOT_GIVEN,
                    tool_choice="auto",
                )

                message = response.choices[0].message
                finish_reason = response.choices[0].finish_reason

                if finish_reason == "stop":
                    return message.content or ""

                elif finish_reason == "tool_calls":
                    # Add GPT's message to history
                    messages.append(message.model_dump())

                    # Process each tool call
                    for tool_call in (message.tool_calls or []):
                        func_name = tool_call.function.name
                        func_args = json.loads(tool_call.function.arguments)

                        print(f"  🔧 GPT calls: {func_name}({json.dumps(func_args)[:80]})")

                        # Execute via MCP
                        mcp_result = await session.call_tool(func_name, func_args)
                        result_text = " ".join(
                            c.text for c in mcp_result.content if hasattr(c, "text")
                        )

                        print(f"  📤 Result: {result_text[:100]}...")

                        # Return tool result to GPT
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_text,
                        })

                else:
                    return f"Unexpected finish_reason: {finish_reason}"


# ─── Demo ──────────────────────────────────────────────────────────────────

async def main():
    print("=" * 55)
    print("  OPENAI GPT + MCP INTEGRATION DEMO")
    print("=" * 55)

    question = "What's the weather in Paris and New York? Which is warmer?"
    print(f"\n{'─' * 55}")
    response = await run_gpt_with_mcp(
        user_message=question,
        server_script="../../04-intermediate/03-weather-server/weather_server.py",
    )
    print(f"\n🤖 GPT: {response}")


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("❌  Please set OPENAI_API_KEY environment variable")
        exit(1)
    asyncio.run(main())
