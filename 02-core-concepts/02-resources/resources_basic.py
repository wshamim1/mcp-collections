"""
MCP Resources — Basic & Advanced Patterns
==========================================
Demonstrates resource patterns:
- Static resources (fixed URI)
- Dynamic resources (URI templates)
- Text vs binary resources
- Resource lists (for browsing)
- Real-world: config, docs, filesystem

Run with:
    mcp dev resources_basic.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("resources-demo")

# ─── Static Resources ─────────────────────────────────────────────────────────
# Static resources have a fixed URI — they don't take parameters.

@mcp.resource("config://app/info")
def get_app_info() -> str:
    """Application information and metadata."""
    return json.dumps({
        "name": "MCP Learning App",
        "version": "1.0.0",
        "author": "MCP Collections",
        "description": "Demonstrating MCP resources",
        "created_at": "2024-01-01",
    }, indent=2)


@mcp.resource("config://app/environment")
def get_environment() -> str:
    """Current runtime environment variables (safe subset)."""
    safe_vars = {
        "PYTHON_VERSION": os.sys.version,
        "PLATFORM": os.sys.platform,
        "CWD": os.getcwd(),
        "HOME": os.path.expanduser("~"),
    }
    return json.dumps(safe_vars, indent=2)


@mcp.resource("docs://help/getting-started")
def get_getting_started_docs() -> str:
    """Getting started guide for this MCP server."""
    return """# Getting Started with this MCP Server

## Available Tools
- Use `list_tools` to see all available tools
- Each tool has a description explaining its purpose

## Available Resources
- config://app/info       — Application metadata
- config://app/environment — Runtime environment
- docs://help/*           — Documentation
- note://{title}         — Access saved notes

## Quick Examples
Ask the AI:
- "Show me the app configuration"
- "What environment is this running in?"
- "Read the note titled 'project-ideas'"
"""


# ─── Dynamic Resources (URI Templates) ────────────────────────────────────────
# Dynamic resources use URI templates with {parameter} placeholders.
# The AI can read different resources by varying the URI.

# In-memory "database" for demo purposes
_notes_db: dict[str, dict] = {
    "project-ideas": {
        "title": "Project Ideas",
        "content": "1. Build a weather bot\n2. Create a code review tool\n3. Make a data analysis assistant",
        "created_at": "2024-01-15",
        "tags": ["projects", "ideas"],
    },
    "meeting-notes": {
        "title": "Meeting Notes",
        "content": "Discussed Q1 roadmap. Key points:\n- Launch v2 by March\n- Add authentication\n- Performance improvements",
        "created_at": "2024-01-20",
        "tags": ["meetings", "planning"],
    },
    "learning-plan": {
        "title": "Learning Plan",
        "content": "Topics to study:\n1. MCP Protocol\n2. LLM integration\n3. Agentic workflows",
        "created_at": "2024-01-22",
        "tags": ["learning", "personal"],
    },
}


@mcp.resource("note://{title}")
def get_note(title: str) -> str:
    """
    Retrieve a saved note by its title/slug.

    URI: note://{title}
    Example: note://project-ideas
    """
    if title not in _notes_db:
        return json.dumps({
            "error": f"Note '{title}' not found",
            "available": list(_notes_db.keys()),
        })

    note = _notes_db[title]
    return f"""# {note['title']}
Created: {note['created_at']}
Tags: {', '.join(note['tags'])}

{note['content']}
"""


@mcp.resource("notes://list")
def list_notes() -> str:
    """List all available notes."""
    notes_list = [
        {
            "slug": slug,
            "title": note["title"],
            "created_at": note["created_at"],
            "tags": note["tags"],
            "uri": f"note://{slug}",
        }
        for slug, note in _notes_db.items()
    ]
    return json.dumps({"notes": notes_list, "count": len(notes_list)}, indent=2)


# ─── File System Resource ──────────────────────────────────────────────────────

@mcp.resource("file://{relative_path}")
def read_project_file(relative_path: str) -> str:
    """
    Read a file from the project directory.

    URI: file://{relative_path}
    Example: file://README.md
    """
    # Security: prevent path traversal attacks
    base_dir = Path.cwd()
    target = (base_dir / relative_path).resolve()

    if not str(target).startswith(str(base_dir)):
        return "Error: Access denied. Cannot read files outside the project directory."

    if not target.exists():
        return f"Error: File not found: {relative_path}"

    if not target.is_file():
        return f"Error: '{relative_path}' is a directory, not a file."

    # Only allow safe file types
    safe_suffixes = {".txt", ".md", ".py", ".json", ".yaml", ".yml", ".toml", ".csv"}
    if target.suffix.lower() not in safe_suffixes:
        return f"Error: File type '{target.suffix}' not supported."

    try:
        content = target.read_text(encoding="utf-8")
        return f"# File: {relative_path}\n\n{content}"
    except UnicodeDecodeError:
        return f"Error: Cannot read '{relative_path}' as text (binary file?)."


@mcp.resource("directory://{path}")
def list_directory(path: str = ".") -> str:
    """
    List the contents of a directory.

    URI: directory://{path}
    Example: directory://.
    """
    base_dir = Path.cwd()
    target = (base_dir / path).resolve()

    if not str(target).startswith(str(base_dir)):
        return "Error: Access denied."

    if not target.exists():
        return f"Error: Directory not found: {path}"

    if not target.is_dir():
        return f"Error: '{path}' is not a directory."

    items = []
    for item in sorted(target.iterdir()):
        if item.name.startswith("."):
            continue
        items.append({
            "name": item.name,
            "type": "directory" if item.is_dir() else "file",
            "size": item.stat().st_size if item.is_file() else None,
        })

    return json.dumps({
        "path": str(target.relative_to(base_dir)),
        "items": items,
        "count": len(items),
    }, indent=2)


# ─── System Status Resource ─────────────────────────────────────────────────

@mcp.resource("system://status")
def get_system_status() -> str:
    """Current system status and health check."""
    return json.dumps({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "server_name": "resources-demo",
        "python_version": os.sys.version.split()[0],
        "uptime": "running",
    }, indent=2)


if __name__ == "__main__":
    mcp.run()
