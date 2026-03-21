"""
Your First MCP Server
=====================
A minimal MCP server demonstrating the core concepts:
- Tools (callable functions)
- Type hints → auto JSON schemas
- Docstrings → tool descriptions for the AI

Run with:
    python simple_server.py

Test with MCP inspector:
    mcp dev simple_server.py
"""

from datetime import datetime
from mcp.server.fastmcp import FastMCP

# ─── Step 1: Create the MCP server ───────────────────────────────────────────
# FastMCP is the high-level API — easiest way to build servers.
# The string argument is the server's name (visible to clients).
mcp = FastMCP("my-first-server")


# ─── Step 2: Define Tools ─────────────────────────────────────────────────────
# Tools are regular Python functions decorated with @mcp.tool()
# The AI model can decide to call these autonomously.

@mcp.tool()
def greet(name: str) -> str:
    """
    Greet a person by name.

    Args:
        name: The name of the person to greet.

    Returns:
        A friendly greeting message.
    """
    return f"Hello, {name}! Welcome to MCP. 🎉"


@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """
    Add two numbers together.

    Args:
        a: The first number.
        b: The second number.

    Returns:
        The sum of a and b.
    """
    return a + b


@mcp.tool()
def get_current_time(timezone: str = "UTC") -> str:
    """
    Get the current date and time.

    Args:
        timezone: Timezone name (currently informational — returns UTC time).

    Returns:
        The current date and time as a formatted string.
    """
    now = datetime.utcnow()
    return f"Current time ({timezone}): {now.strftime('%Y-%m-%d %H:%M:%S')}"


@mcp.tool()
def reverse_string(text: str) -> str:
    """
    Reverse a string.

    Args:
        text: The string to reverse.

    Returns:
        The reversed string.
    """
    return text[::-1]


@mcp.tool()
def count_words(text: str) -> dict:
    """
    Count words and characters in a text.

    Args:
        text: The input text to analyze.

    Returns:
        A dictionary with word_count and char_count.
    """
    words = text.split()
    return {
        "word_count": len(words),
        "char_count": len(text),
        "char_count_no_spaces": len(text.replace(" ", "")),
    }


# ─── Step 3: Run the server ───────────────────────────────────────────────────
# mcp.run() starts the server using stdio transport by default.
# This is perfect for local development and Claude Desktop.
if __name__ == "__main__":
    print("Starting my-first-server...")
    print("Available tools: greet, add_numbers, get_current_time, reverse_string, count_words")
    mcp.run()
