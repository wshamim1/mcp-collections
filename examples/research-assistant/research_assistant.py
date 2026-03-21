"""
Complete Example: AI Research Assistant
========================================
A research assistant that:
1. Searches Wikipedia for information
2. Fetches web pages
3. Summarizes and synthesizes findings
4. Saves notes to a file

This shows how to combine multiple tools into a useful agent.

Dependencies:
    pip install mcp httpx

Run:
    mcp dev research_assistant.py   # Explore tools
    python research_assistant.py    # Run demo
"""

import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import httpx
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("research-assistant")

NOTES_DIR = Path(__file__).parent / "notes"
NOTES_DIR.mkdir(exist_ok=True)


# ─── Wikipedia Tool ──────────────────────────────────────────────────────────

@mcp.tool()
async def search_wikipedia(query: str, max_results: int = 3) -> dict:
    """
    Search Wikipedia and return article summaries.

    Args:
        query: The search query.
        max_results: Number of results to return (default: 3).

    Returns:
        List of matching articles with titles and summaries.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Search for article titles
        search_response = await client.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "opensearch",
                "search": query,
                "limit": max_results,
                "format": "json",
            },
        )
        search_data = search_response.json()
        titles = search_data[1]
        descriptions = search_data[2]
        urls = search_data[3]

        results = []
        for title, desc, url in zip(titles, descriptions, urls):
            results.append({
                "title": title,
                "description": desc,
                "url": url,
            })

    return {"query": query, "results": results, "count": len(results)}


@mcp.tool()
async def get_wikipedia_article(title: str) -> dict:
    """
    Get the full summary of a Wikipedia article.

    Args:
        title: The Wikipedia article title (exact or close match).

    Returns:
        Article extract with introduction and key facts.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "titles": title,
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "format": "json",
                "redirects": True,
            },
        )
        data = response.json()
        pages = data.get("query", {}).get("pages", {})

        for page_id, page in pages.items():
            if page_id == "-1":
                return {"error": f"Article '{title}' not found on Wikipedia."}

            extract = page.get("extract", "")
            # Truncate to first 1500 chars for manageable size
            if len(extract) > 1500:
                extract = extract[:1500] + "...\n[Truncated — see full article for more]"

            return {
                "title": page.get("title"),
                "extract": extract,
                "url": f"https://en.wikipedia.org/wiki/{quote(page.get('title', title))}",
            }

    return {"error": "Failed to fetch article."}


# ─── Web Fetch Tool ──────────────────────────────────────────────────────────

@mcp.tool()
async def fetch_webpage_text(url: str, max_length: int = 2000) -> dict:
    """
    Fetch a webpage and return its text content.

    Args:
        url: The URL to fetch. Must start with https://.
        max_length: Maximum characters to return.

    Returns:
        Page title and text content.
    """
    # Security: only allow HTTPS
    if not url.startswith("https://"):
        return {"error": "Only HTTPS URLs are allowed."}

    # Block private/internal networks (prevent SSRF)
    import ipaddress
    try:
        from urllib.parse import urlparse
        host = urlparse(url).hostname
        try:
            ip = ipaddress.ip_address(host)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return {"error": "Access to private/internal addresses is not allowed."}
        except ValueError:
            pass  # Not an IP address — hostname is fine
    except Exception:
        pass

    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            headers={"User-Agent": "ResearchBot/1.0"},
            max_redirects=3,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "html" not in content_type and "text" not in content_type:
                return {"error": f"Unsupported content type: {content_type}"}

            text = response.text
            # Strip HTML tags
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+", " ", text).strip()

            if len(text) > max_length:
                text = text[:max_length] + "...[truncated]"

            return {
                "url": url,
                "content_length": len(response.text),
                "text": text,
                "status_code": response.status_code,
            }
    except httpx.TimeoutException:
        return {"error": "Request timed out after 10 seconds."}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to fetch page: {str(e)}"}


# ─── Note-Taking Tools ────────────────────────────────────────────────────────

@mcp.tool()
def save_research_note(title: str, content: str, tags: list[str] = None) -> dict:
    """
    Save a research note to disk.

    Args:
        title: Note title (used as filename).
        content: Note content in markdown format.
        tags: Optional list of tags for organization.

    Returns:
        Confirmation with file path.
    """
    # Sanitize filename
    safe_title = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "-").lower()
    if not safe_title:
        return {"error": "Invalid note title."}

    filename = f"{datetime.now().strftime('%Y%m%d')}-{safe_title}.md"
    note_path = NOTES_DIR / filename

    tags_line = f"\nTags: {', '.join(tags)}" if tags else ""
    full_content = f"# {title}\n\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M')}{tags_line}\n\n{content}\n"

    note_path.write_text(full_content, encoding="utf-8")

    return {
        "success": True,
        "file": str(note_path),
        "title": title,
        "bytes_written": len(full_content),
    }


@mcp.tool()
def list_research_notes() -> dict:
    """List all saved research notes."""
    notes = []
    for f in sorted(NOTES_DIR.glob("*.md")):
        notes.append({
            "filename": f.name,
            "size_bytes": f.stat().st_size,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        })
    return {"notes": notes, "count": len(notes)}


@mcp.tool()
def read_research_note(filename: str) -> dict:
    """
    Read a saved research note.

    Args:
        filename: The note filename (from list_research_notes).
    """
    # Validate filename — no path traversal
    if "/" in filename or "\\" in filename or ".." in filename:
        return {"error": "Invalid filename."}

    note_path = NOTES_DIR / filename
    if not note_path.exists():
        return {"error": f"Note '{filename}' not found."}

    return {
        "filename": filename,
        "content": note_path.read_text(encoding="utf-8"),
    }


if __name__ == "__main__":
    print("Research Assistant MCP Server")
    print(f"Notes directory: {NOTES_DIR}")
    print("\nAvailable tools:")
    print("  • search_wikipedia    — Search for topics")
    print("  • get_wikipedia_article — Get full article")
    print("  • fetch_webpage_text  — Read web pages")
    print("  • save_research_note  — Save findings")
    print("  • list_research_notes — Browse saved notes")
    print("\nTest with: mcp dev research_assistant.py")
    mcp.run()
