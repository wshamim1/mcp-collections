"""
Filesystem MCP Server
======================
A practical MCP server for AI-assisted file operations.
All operations are sandboxed to BASE_DIR for security.

Features:
- read_file     — Read file contents
- write_file    — Create or overwrite a file
- list_dir      — List directory contents
- search_files  — Find files by name pattern
- file_info     — Get file metadata
- move_file     — Move/rename files
- delete_file   — Delete files (with confirmation flag)
- create_dir    — Create directories

Security:
- All paths validated against BASE_DIR (no path traversal)
- File size limits (default: 1MB read, 512KB write)
- Allowed file extensions whitelist
- No symlink following outside sandbox

Run with:
    python filesystem_server.py

Or set custom base directory:
    BASE_DIR=/tmp/workspace python filesystem_server.py
"""

import fnmatch
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ─── Configuration ─────────────────────────────────────────────────────────
BASE_DIR = Path(os.environ.get("BASE_DIR", Path.cwd())).resolve()
MAX_READ_SIZE = int(os.environ.get("MAX_READ_SIZE", 1024 * 1024))   # 1 MB
MAX_WRITE_SIZE = int(os.environ.get("MAX_WRITE_SIZE", 512 * 1024))  # 512 KB

READABLE_EXTENSIONS = {
    ".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml",
    ".toml", ".cfg", ".ini", ".env.example", ".csv", ".html", ".css",
    ".sh", ".dockerfile", ".sql", ".log", ".rst", ".xml",
}

WRITABLE_EXTENSIONS = {
    ".txt", ".md", ".py", ".json", ".yaml", ".yml", ".toml", ".csv",
    ".html", ".css", ".js", ".ts", ".sql",
}

mcp = FastMCP("filesystem-server")


# ─── Security Helper ──────────────────────────────────────────────────────────

def safe_path(relative_path: str) -> Path:
    """
    Resolve a relative path against BASE_DIR, raising on traversal attempts.
    Returns absolute Path if safe, raises ValueError if unsafe.
    """
    # Expand ~ and resolve the path fully
    resolved = (BASE_DIR / relative_path).resolve()

    # Prevent path traversal outside BASE_DIR
    if not str(resolved).startswith(str(BASE_DIR)):
        raise ValueError(
            f"Access denied: '{relative_path}' resolves outside the allowed directory."
        )

    return resolved


# ─── Tools ─────────────────────────────────────────────────────────────────

@mcp.tool()
def read_file(path: str, encoding: str = "utf-8", max_lines: Optional[int] = None) -> dict:
    """
    Read the contents of a file.

    Args:
        path: Relative path from the base directory.
        encoding: File encoding (default: utf-8).
        max_lines: If set, return only the first N lines.

    Returns:
        Dictionary with 'content', 'lines', 'size_bytes', and 'path' keys.
    """
    try:
        target = safe_path(path)
    except ValueError as e:
        return {"error": str(e)}

    if not target.exists():
        return {"error": f"File not found: {path}"}
    if not target.is_file():
        return {"error": f"'{path}' is a directory, not a file."}
    if target.suffix.lower() not in READABLE_EXTENSIONS:
        return {"error": f"File extension '{target.suffix}' is not allowed for reading."}

    size = target.stat().st_size
    if size > MAX_READ_SIZE:
        return {
            "error": f"File too large ({size:,} bytes). Maximum: {MAX_READ_SIZE:,} bytes.",
            "size_bytes": size,
        }

    try:
        content = target.read_text(encoding=encoding)
    except UnicodeDecodeError:
        return {"error": f"Cannot decode '{path}' as {encoding}. Try a different encoding."}

    lines = content.splitlines()
    if max_lines is not None:
        lines = lines[:max_lines]
        content = "\n".join(lines)

    return {
        "path": path,
        "content": content,
        "line_count": len(lines),
        "size_bytes": size,
        "truncated": max_lines is not None and len(content.splitlines()) == max_lines,
    }


@mcp.tool()
def write_file(path: str, content: str, overwrite: bool = False) -> dict:
    """
    Write content to a file. Creates the file if it doesn't exist.

    Args:
        path: Relative path from the base directory.
        content: The content to write.
        overwrite: Set to true to allow overwriting existing files.

    Returns:
        Success or error message.
    """
    try:
        target = safe_path(path)
    except ValueError as e:
        return {"error": str(e)}

    if target.suffix.lower() not in WRITABLE_EXTENSIONS:
        return {"error": f"File extension '{target.suffix}' is not allowed for writing."}

    if len(content.encode("utf-8")) > MAX_WRITE_SIZE:
        return {"error": f"Content too large. Maximum: {MAX_WRITE_SIZE:,} bytes."}

    if target.exists() and not overwrite:
        return {"error": f"File already exists: '{path}'. Set overwrite=true to replace it."}

    # Create parent directories if needed
    target.parent.mkdir(parents=True, exist_ok=True)

    target.write_text(content, encoding="utf-8")

    return {
        "success": True,
        "path": path,
        "size_bytes": target.stat().st_size,
        "created": not target.exists(),
    }


@mcp.tool()
def list_dir(path: str = ".", show_hidden: bool = False) -> dict:
    """
    List the contents of a directory.

    Args:
        path: Relative path to the directory (default: current base dir).
        show_hidden: Whether to include hidden files (starting with .).

    Returns:
        Dictionary with lists of 'files' and 'directories'.
    """
    try:
        target = safe_path(path)
    except ValueError as e:
        return {"error": str(e)}

    if not target.exists():
        return {"error": f"Directory not found: {path}"}
    if not target.is_dir():
        return {"error": f"'{path}' is not a directory."}

    files = []
    directories = []

    for item in sorted(target.iterdir()):
        if not show_hidden and item.name.startswith("."):
            continue

        stat = item.stat()
        entry = {
            "name": item.name,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }

        if item.is_dir():
            entry["type"] = "directory"
            directories.append(entry)
        else:
            entry["type"] = "file"
            entry["size_bytes"] = stat.st_size
            entry["extension"] = item.suffix.lower()
            files.append(entry)

    return {
        "path": path,
        "directories": directories,
        "files": files,
        "total_dirs": len(directories),
        "total_files": len(files),
    }


@mcp.tool()
def search_files(pattern: str, search_dir: str = ".", recursive: bool = True) -> dict:
    """
    Search for files matching a glob pattern.

    Args:
        pattern: Filename pattern with wildcards (e.g., "*.py", "test_*").
        search_dir: Directory to search in (default: base dir).
        recursive: Search subdirectories recursively.

    Returns:
        List of matching file paths.
    """
    try:
        target = safe_path(search_dir)
    except ValueError as e:
        return {"error": str(e)}

    if not target.is_dir():
        return {"error": f"'{search_dir}' is not a directory."}

    matches = []
    glob_method = target.rglob if recursive else target.glob

    for item in glob_method(pattern):
        if item.is_file():
            try:
                rel_path = item.relative_to(BASE_DIR)
                matches.append({
                    "path": str(rel_path),
                    "size_bytes": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                })
            except ValueError:
                pass  # Skip files outside BASE_DIR

    return {
        "pattern": pattern,
        "search_dir": search_dir,
        "results": matches,
        "count": len(matches),
    }


@mcp.tool()
def file_info(path: str) -> dict:
    """
    Get detailed metadata about a file or directory.

    Args:
        path: Relative path from the base directory.

    Returns:
        File metadata including size, timestamps, and permissions.
    """
    try:
        target = safe_path(path)
    except ValueError as e:
        return {"error": str(e)}

    if not target.exists():
        return {"error": f"Not found: {path}"}

    stat = target.stat()
    return {
        "path": path,
        "name": target.name,
        "type": "directory" if target.is_dir() else "file",
        "extension": target.suffix.lower() if target.is_file() else None,
        "size_bytes": stat.st_size,
        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        "is_readable": os.access(target, os.R_OK),
        "is_writable": os.access(target, os.W_OK),
    }


@mcp.tool()
def move_file(source: str, destination: str) -> dict:
    """
    Move or rename a file.

    Args:
        source: Source file path (relative).
        destination: Destination file path (relative).

    Returns:
        Success or error message.
    """
    try:
        src = safe_path(source)
        dst = safe_path(destination)
    except ValueError as e:
        return {"error": str(e)}

    if not src.exists():
        return {"error": f"Source not found: {source}"}
    if dst.exists():
        return {"error": f"Destination already exists: {destination}. Remove it first."}

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))

    return {"success": True, "moved_from": source, "moved_to": destination}


@mcp.tool()
def create_directory(path: str) -> dict:
    """
    Create a directory (and any missing parent directories).

    Args:
        path: Relative path of the directory to create.

    Returns:
        Success or error message.
    """
    try:
        target = safe_path(path)
    except ValueError as e:
        return {"error": str(e)}

    if target.exists():
        return {"error": f"Already exists: {path}"}

    target.mkdir(parents=True)
    return {"success": True, "created": path}


# ─── Resources ────────────────────────────────────────────────────────────────

@mcp.resource("fs://base-dir")
def get_base_dir_info() -> str:
    """Information about the filesystem server's base directory."""
    return json.dumps({
        "base_directory": str(BASE_DIR),
        "max_read_size_bytes": MAX_READ_SIZE,
        "max_write_size_bytes": MAX_WRITE_SIZE,
        "readable_extensions": sorted(READABLE_EXTENSIONS),
        "writable_extensions": sorted(WRITABLE_EXTENSIONS),
    }, indent=2)


if __name__ == "__main__":
    print(f"Filesystem MCP Server")
    print(f"Base directory: {BASE_DIR}")
    print(f"Max read size:  {MAX_READ_SIZE:,} bytes")
    mcp.run()
