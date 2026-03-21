"""
Multi-Model Router — Switch Between AI Models Dynamically
===========================================================
A unified interface that routes requests to different AI models
based on task type, cost, or availability.

Router strategies:
1. Task-based routing  — complex → Claude, simple → GPT-3.5
2. Cost-based routing  — try cheap model first, escalate if needed
3. Fallback routing    — use Ollama if API keys not available
4. Load routing        — round-robin across models

Use case: build one agent that works with any available model,
gracefully degrading from API models to local Ollama.

Run:
    python multi_model_router.py
"""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ─── Model Definitions ────────────────────────────────────────────────────────

class ModelProvider(str, Enum):
    CLAUDE = "claude"
    OPENAI = "openai"
    OLLAMA = "ollama"


@dataclass
class ModelConfig:
    name: str
    provider: ModelProvider
    model_id: str
    cost_per_1k_tokens: float  # USD, approximate
    supports_tools: bool = True
    max_context_tokens: int = 128000
    is_local: bool = False


# Available models registry
MODELS = {
    "claude-sonnet": ModelConfig(
        name="claude-sonnet",
        provider=ModelProvider.CLAUDE,
        model_id="claude-3-5-sonnet-20241022",
        cost_per_1k_tokens=0.003,
    ),
    "claude-haiku": ModelConfig(
        name="claude-haiku",
        provider=ModelProvider.CLAUDE,
        model_id="claude-3-5-haiku-20241022",
        cost_per_1k_tokens=0.0008,
    ),
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        provider=ModelProvider.OPENAI,
        model_id="gpt-4o",
        cost_per_1k_tokens=0.0025,
    ),
    "gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini",
        provider=ModelProvider.OPENAI,
        model_id="gpt-4o-mini",
        cost_per_1k_tokens=0.00015,
    ),
    "llama3.2": ModelConfig(
        name="llama3.2",
        provider=ModelProvider.OLLAMA,
        model_id="llama3.2",
        cost_per_1k_tokens=0.0,  # Free (local)
        is_local=True,
    ),
    "mistral-nemo": ModelConfig(
        name="mistral-nemo",
        provider=ModelProvider.OLLAMA,
        model_id="mistral-nemo",
        cost_per_1k_tokens=0.0,
        is_local=True,
    ),
}


# ─── Router Strategies ────────────────────────────────────────────────────────

def select_model_by_availability() -> ModelConfig:
    """
    Try models in order of preference, use first available.
    Priority: Claude → OpenAI → Ollama (local fallback)
    """
    if os.environ.get("ANTHROPIC_API_KEY"):
        print("  → Using Claude (API key found)")
        return MODELS["claude-sonnet"]

    if os.environ.get("OPENAI_API_KEY"):
        print("  → Using GPT-4o (API key found)")
        return MODELS["gpt-4o"]

    print("  → Using Ollama/llama3.2 (local fallback)")
    return MODELS["llama3.2"]


def select_model_by_task(task_description: str) -> ModelConfig:
    """
    Choose model based on task complexity keywords.
    """
    task_lower = task_description.lower()

    # Complex reasoning tasks → best model
    complex_keywords = ["analyze", "compare", "explain", "reason", "code", "debug", "review"]
    if any(k in task_lower for k in complex_keywords):
        if os.environ.get("ANTHROPIC_API_KEY"):
            print("  → Complex task: using Claude Sonnet")
            return MODELS["claude-sonnet"]

    # Simple tasks → faster/cheaper model
    simple_keywords = ["what is", "list", "show", "get", "fetch", "find"]
    if any(k in task_lower for k in simple_keywords):
        if os.environ.get("OPENAI_API_KEY"):
            print("  → Simple task: using GPT-4o-mini")
            return MODELS["gpt-4o-mini"]
        if os.environ.get("ANTHROPIC_API_KEY"):
            print("  → Simple task: using Claude Haiku")
            return MODELS["claude-haiku"]

    # Default to availability-based selection
    return select_model_by_availability()


def select_cheapest_model() -> ModelConfig:
    """Always use the cheapest available model."""
    available = []

    if os.environ.get("ANTHROPIC_API_KEY"):
        available.append(MODELS["claude-haiku"])
    if os.environ.get("OPENAI_API_KEY"):
        available.append(MODELS["gpt-4o-mini"])

    # Local models are free!
    available.append(MODELS["llama3.2"])

    cheapest = min(available, key=lambda m: m.cost_per_1k_tokens)
    print(f"  → Cheapest available: {cheapest.name} (${cheapest.cost_per_1k_tokens}/1k tokens)")
    return cheapest


# ─── Universal Model Caller ──────────────────────────────────────────────────

async def call_model(
    model_config: ModelConfig,
    messages: list[dict],
    tools: list[dict],
) -> tuple[str | None, list[dict]]:
    """
    Call any model with unified interface.
    Returns (final_text_or_None, tool_calls_list)
    """
    provider = model_config.provider

    if provider == ModelProvider.CLAUDE:
        return await _call_claude(model_config.model_id, messages, tools)
    elif provider == ModelProvider.OPENAI:
        return await _call_openai(model_config.model_id, messages, tools)
    elif provider == ModelProvider.OLLAMA:
        return await _call_ollama(model_config.model_id, messages, tools)
    else:
        raise ValueError(f"Unknown provider: {provider}")


async def _call_claude(model_id: str, messages: list[dict], tools: list[dict]):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model=model_id,
        max_tokens=2048,
        tools=tools,
        messages=messages,
    )

    if response.stop_reason == "end_turn":
        text = " ".join(b.text for b in response.content if hasattr(b, "text"))
        return text, []
    elif response.stop_reason == "tool_use":
        tool_calls = [
            {"id": b.id, "name": b.name, "arguments": b.input}
            for b in response.content if b.type == "tool_use"
        ]
        return None, tool_calls
    return None, []


async def _call_openai(model_id: str, messages: list[dict], tools: list[dict]):
    import openai
    client = openai.AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

    # Convert Claude tool format to OpenAI format if needed
    oai_tools = [
        t if "type" in t else {"type": "function", "function": t}
        for t in tools
    ]

    response = await client.chat.completions.create(
        model=model_id,
        messages=messages,
        tools=oai_tools or openai.NOT_GIVEN,
    )

    choice = response.choices[0]
    if choice.finish_reason == "stop":
        return choice.message.content, []
    elif choice.finish_reason == "tool_calls":
        tool_calls = [
            {
                "id": tc.id,
                "name": tc.function.name,
                "arguments": json.loads(tc.function.arguments),
            }
            for tc in (choice.message.tool_calls or [])
        ]
        return None, tool_calls
    return None, []


async def _call_ollama(model_id: str, messages: list[dict], tools: list[dict]):
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/chat",
            json={"model": model_id, "messages": messages, "tools": tools, "stream": False},
        )
        data = response.json()
        message = data.get("message", {})
        tool_calls = message.get("tool_calls", [])

        if not tool_calls:
            return message.get("content", ""), []

        formatted = [
            {
                "id": f"ollama-{i}",
                "name": tc["function"]["name"],
                "arguments": tc["function"].get("arguments", {}),
            }
            for i, tc in enumerate(tool_calls)
        ]
        return None, formatted


# ─── Multi-Model Agent ────────────────────────────────────────────────────────

async def run_with_any_model(
    user_message: str,
    server_script: str,
    routing_strategy: str = "availability",
) -> dict:
    """
    Run a query using the best available model + MCP tools.

    Args:
        user_message: User's question.
        server_script: Path to MCP server.
        routing_strategy: "availability", "task", or "cheapest".

    Returns:
        Dict with response and model used.
    """
    # Select model
    if routing_strategy == "task":
        model_config = select_model_by_task(user_message)
    elif routing_strategy == "cheapest":
        model_config = select_cheapest_model()
    else:
        model_config = select_model_by_availability()

    print(f"  🤖 Selected model: {model_config.name} ({model_config.provider.value})")

    server_params = StdioServerParameters(command="python", args=[server_script])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()

            # Build tools in Claude format (all providers accept this structure)
            tools = [
                {
                    "name": t.name,
                    "description": t.description or t.name,
                    "input_schema": t.inputSchema,
                }
                for t in tools_result.tools
            ]

            messages = [
                {"role": "user", "content": user_message},
            ]

            for _ in range(5):
                final_text, tool_calls = await call_model(model_config, messages, tools)

                if final_text:
                    return {
                        "response": final_text,
                        "model_used": model_config.name,
                        "provider": model_config.provider.value,
                    }

                if not tool_calls:
                    break

                for tc in tool_calls:
                    print(f"    🔧 {model_config.name} calls: {tc['name']}")
                    mcp_result = await session.call_tool(tc["name"], tc["arguments"])
                    result_text = " ".join(c.text for c in mcp_result.content if hasattr(c, "text"))

                    messages.append({"role": "assistant", "content": json.dumps(tool_calls)})
                    messages.append({"role": "user", "content": f"Tool result: {result_text}"})

    return {"response": "No response generated.", "model_used": model_config.name}


# ─── Demo ──────────────────────────────────────────────────────────────────

async def main():
    print("=" * 55)
    print("  MULTI-MODEL ROUTER DEMO")
    print("=" * 55)

    # Show configured models
    print("\n📋 Model availability:")
    print(f"  Claude:  {'✅' if os.environ.get('ANTHROPIC_API_KEY') else '❌ (no API key)'}")
    print(f"  OpenAI:  {'✅' if os.environ.get('OPENAI_API_KEY') else '❌ (no API key)'}")
    print(f"  Ollama:  ✅ (local, always available if running)")

    question = "What's the current weather in Berlin?"
    print(f"\n{'─' * 55}")
    print(f"💬 Question: {question}")
    print(f"📡 Strategy: availability-based routing\n")

    result = await run_with_any_model(
        user_message=question,
        server_script="../../04-intermediate/03-weather-server/weather_server.py",
        routing_strategy="availability",
    )

    print(f"\n🤖 Response ({result['model_used']}): {result['response']}")


if __name__ == "__main__":
    asyncio.run(main())
