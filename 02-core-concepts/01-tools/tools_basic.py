"""
MCP Tools — Basic Patterns
===========================
Demonstrates the essential patterns for defining MCP tools:
- Simple string/number tools
- Tools with optional parameters
- Tools returning complex objects
- Tools with validation using Pydantic
- Async tools for I/O-bound work

Run with:
    mcp dev tools_basic.py
"""

import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Optional

import httpx
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("tools-demo")


# ─── Pattern 1: Simple Tools ─────────────────────────────────────────────────

@mcp.tool()
def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Convert a temperature from Celsius to Fahrenheit.

    Args:
        celsius: Temperature in degrees Celsius.

    Returns:
        Temperature in degrees Fahrenheit.
    """
    return (celsius * 9 / 5) + 32


@mcp.tool()
def is_palindrome(text: str) -> bool:
    """
    Check if a string is a palindrome (reads the same forwards and backwards).

    Args:
        text: The string to check.

    Returns:
        True if palindrome, False otherwise.
    """
    cleaned = text.lower().replace(" ", "")
    return cleaned == cleaned[::-1]


# ─── Pattern 2: Optional Parameters ──────────────────────────────────────────

@mcp.tool()
def format_date(
    year: int,
    month: int,
    day: int,
    format_string: str = "%B %d, %Y",
) -> str:
    """
    Format a date into a human-readable string.

    Args:
        year: The year (e.g., 2024).
        month: The month (1-12).
        day: The day (1-31).
        format_string: Python strftime format. Defaults to "Month DD, YYYY".

    Returns:
        The formatted date string.
    """
    date = datetime(year, month, day)
    return date.strftime(format_string)


# ─── Pattern 3: Returning Structured Data ────────────────────────────────────

@mcp.tool()
def analyze_text(text: str) -> dict:
    """
    Analyze text and return statistics.

    Args:
        text: The text to analyze.

    Returns:
        A dictionary with text statistics including word count,
        sentence count, average word length, and most common words.
    """
    words = text.lower().split()
    sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]

    word_freq: dict[str, int] = {}
    for word in words:
        clean = word.strip(".,!?;:'\"")
        word_freq[clean] = word_freq.get(clean, 0) + 1

    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "character_count": len(text),
        "avg_word_length": round(sum(len(w) for w in words) / max(len(words), 1), 2),
        "top_words": [{"word": w, "count": c} for w, c in top_words],
    }


# ─── Pattern 4: Enum Parameters ───────────────────────────────────────────────

class SortOrder(str, Enum):
    ASCENDING = "ascending"
    DESCENDING = "descending"


@mcp.tool()
def sort_numbers(numbers: list[float], order: SortOrder = SortOrder.ASCENDING) -> list[float]:
    """
    Sort a list of numbers.

    Args:
        numbers: List of numbers to sort.
        order: Sort direction — "ascending" or "descending".

    Returns:
        The sorted list.
    """
    return sorted(numbers, reverse=(order == SortOrder.DESCENDING))


# ─── Pattern 5: Pydantic Input Models ─────────────────────────────────────────

class ContactInfo(BaseModel):
    name: str = Field(description="Full name of the contact")
    email: str = Field(description="Email address")
    phone: Optional[str] = Field(None, description="Phone number (optional)")
    notes: Optional[str] = Field(None, description="Additional notes")


@mcp.tool()
def create_contact_card(contact: ContactInfo) -> str:
    """
    Format contact information into a readable card.

    Args:
        contact: Contact information including name, email, optional phone and notes.

    Returns:
        A formatted contact card as text.
    """
    card = f"""
╔══════════════════════════════════╗
  CONTACT CARD
╠══════════════════════════════════╣
  Name:  {contact.name}
  Email: {contact.email}"""
    if contact.phone:
        card += f"\n  Phone: {contact.phone}"
    if contact.notes:
        card += f"\n  Notes: {contact.notes}"
    card += "\n╚══════════════════════════════════╝"
    return card


# ─── Pattern 6: Async Tools for I/O ───────────────────────────────────────────

@mcp.tool()
async def fetch_json(url: str) -> dict:
    """
    Fetch JSON data from a URL.

    Args:
        url: The URL to fetch JSON from.

    Returns:
        The parsed JSON response as a dictionary.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def check_url_status(url: str) -> dict:
    """
    Check if a URL is reachable and return its HTTP status.

    Args:
        url: The URL to check.

    Returns:
        A dictionary with 'status_code', 'ok', and 'response_time_ms'.
    """
    import time
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.head(url)
        elapsed_ms = round((time.monotonic() - start) * 1000, 2)
        return {
            "url": url,
            "status_code": response.status_code,
            "ok": response.status_code < 400,
            "response_time_ms": elapsed_ms,
        }
    except Exception as e:
        return {
            "url": url,
            "status_code": None,
            "ok": False,
            "error": str(e),
        }


# ─── Pattern 7: Tool with Error Handling ──────────────────────────────────────

@mcp.tool()
def safe_divide(numerator: float, denominator: float) -> dict:
    """
    Safely divide two numbers, handling division by zero.

    Args:
        numerator: The number to divide.
        denominator: The number to divide by.

    Returns:
        A dictionary with 'result' on success or 'error' on failure.
    """
    if denominator == 0:
        return {"error": "Division by zero is not allowed.", "result": None}
    return {"result": numerator / denominator, "error": None}


if __name__ == "__main__":
    mcp.run()
