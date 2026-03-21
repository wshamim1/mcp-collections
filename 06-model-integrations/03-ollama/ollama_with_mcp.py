"""
Ollama + MCP Integration — Local Models
=========================================
Run MCP tools with completely local, open-source models via Ollama.
No API keys needed — everything runs on your machine!

Supported models that work well with tools:
- llama3.2          (fast, good tool use)
- llama3.1:70b      (best quality, needs GPU)
- mistral-nemo      (excellent tool following)
- qwen2.5:7b        (great multilingual + tools)
- deepseek-r1:8b    (strong reasoning)

Install Ollama: https://ollama.ai
Pull a model:   ollama pull llama3.2

Run:
    python ollama_with_mcp.py
"""

import asyncio
import json
import os
from typing import Any

import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")


# ─── Ollama API Client ───────────────────────────────────────────────────────

class OllamaClient:
    """Minimal client for Ollama's chat API with tool support."""

    def __init__(self, base_url: str = OLLAMA_URL):
        self.base_url = base_url

    async def chat(
        self,
        model: str,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict:
        """Send a chat request to Ollama."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def list_models(self) -> list[str]:
        """List locally available models."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{self.base_url}/api/tags")
            data = response.json()
            return [m["name"] for m in data.get("models", [])]

    async def is_running(self) -> bool:
        """Check if Ollama is running."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.get(f"{self.base_url}/api/tags")
            return True
        except Exception:
            return False


# ─── MCP Tool Conversion for Ollama ──────────────────────────────────────────

def mcp_tool_to_ollama_format(mcp_tool) -> dict:
    """
    Convert MCP tool to Ollama's tool format.
    Ollama uses the same OpenAI-compatible format.
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

async def run_ollama_with_mcp(
    user_message: str,
    server_script: str,
    model: str = OLLAMA_MODEL,
) -> str:
    """
    Run an Ollama model with tools from an MCP server.
    """
    ollama = OllamaClient()

    if not await ollama.is_running():
        return (
            "❌ Ollama is not running. Start it with: ollama serve\n"
            "   Then pull a model: ollama pull llama3.2"
        )

    server_params = StdioServerParameters(command="python", args=[server_script])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            ollama_tools = [mcp_tool_to_ollama_format(t) for t in tools_result.tools]

            print(f"🦙 Using model: {model}")
            print(f"🔧 Loaded {len(ollama_tools)} tools")
            print(f"💬 User: {user_message}\n")

            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Use the available tools to answer questions accurately.",
                },
                {"role": "user", "content": user_message},
            ]

            max_iterations = 5  # Prevent infinite loops
            iteration = 0

            while iteration < max_iterations:
                iteration += 1
                response = await ollama.chat(model=model, messages=messages, tools=ollama_tools)

                response_message = response.get("message", {})
                tool_calls = response_message.get("tool_calls", [])

                if not tool_calls:
                    # No more tool calls → final answer
                    return response_message.get("content", "No response generated.")

                # Add assistant message
                messages.append(response_message)

                # Process tool calls
                for tool_call in tool_calls:
                    func = tool_call.get("function", {})
                    func_name = func.get("name", "")
                    func_args = func.get("arguments", {})

                    if isinstance(func_args, str):
                        try:
                            func_args = json.loads(func_args)
                        except json.JSONDecodeError:
                            func_args = {}

                    print(f"  🔧 {model} calls: {func_name}({json.dumps(func_args)[:80]})")

                    mcp_result = await session.call_tool(func_name, func_args)
                    result_text = " ".join(
                        c.text for c in mcp_result.content if hasattr(c, "text")
                    )

                    print(f"  📤 Result: {result_text[:100]}...")

                    messages.append({
                        "role": "tool",
                        "content": result_text,
                    })

            return "Max iterations reached without a final answer."


# ─── Demo ──────────────────────────────────────────────────────────────────

async def main():
    print("=" * 55)
    print("  OLLAMA (LOCAL MODEL) + MCP DEMO")
    print("=" * 55)

    ollama = OllamaClient()
    if not await ollama.is_running():
        print("\n⚠️  Ollama is not running.")
        print("   Install:  https://ollama.ai")
        print("   Start:    ollama serve")
        print("   Pull:     ollama pull llama3.2")
        return

    available = await ollama.list_models()
    print(f"\n📦 Available models: {', '.join(available[:5])}")

    question = "What's the weather in Tokyo right now?"
    print(f"\n{'─' * 55}")
    response = await run_ollama_with_mcp(
        user_message=question,
        server_script="../../04-intermediate/03-weather-server/weather_server.py",
    )
    print(f"\n🦙 {OLLAMA_MODEL}: {response}")


if __name__ == "__main__":
    asyncio.run(main())
