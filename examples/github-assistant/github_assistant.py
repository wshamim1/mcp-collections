"""
GitHub Assistant — MCP Example
==============================
A practical read-only MCP server for GitHub workflows.

Features:
- Search public repositories
- Get repository metadata
- List issues and pull requests
- Read issue details
- Fetch repository file contents

Environment:
- Optional: GITHUB_TOKEN for higher rate limits and private repo access

Run with:
    mcp dev github_assistant.py
"""

import base64
import os
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("github-assistant")

GITHUB_API_BASE = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USER_AGENT = "mcp-collections-github-example"
MAX_ITEMS = 20
MAX_FILE_CHARS = 12000


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


async def _github_request(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{GITHUB_API_BASE}{path}"
    async with httpx.AsyncClient(timeout=20.0, headers=_headers()) as client:
        response = await client.get(url, params=params)

    if response.status_code == 404:
        return {"error": "GitHub resource not found."}

    if response.status_code == 403:
        rate_remaining = response.headers.get("X-RateLimit-Remaining")
        if rate_remaining == "0":
            return {
                "error": "GitHub API rate limit exceeded. Add GITHUB_TOKEN for higher limits.",
                "rate_limit_remaining": rate_remaining,
            }
        return {"error": "GitHub API access forbidden. Check token permissions if using private resources."}

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        return {"error": f"GitHub API request failed: {exc.response.status_code}"}

    return response.json()


@mcp.tool()
async def search_repositories(query: str, sort: str = "stars", limit: int = 5) -> dict[str, Any]:
    """
    Search GitHub repositories by keyword.

    Args:
        query: Search query, for example "mcp python" or "fastapi template".
        sort: Sort order, such as "stars", "forks", or "updated".
        limit: Maximum number of repositories to return (1-20).

    Returns:
        Matching repositories with key metadata.
    """
    limit = max(1, min(limit, MAX_ITEMS))
    data = await _github_request(
        "/search/repositories",
        params={"q": query, "sort": sort, "order": "desc", "per_page": limit},
    )

    if "error" in data:
        return data

    items = []
    for repo in data.get("items", []):
        items.append(
            {
                "full_name": repo["full_name"],
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "open_issues": repo.get("open_issues_count"),
                "url": repo.get("html_url"),
                "updated_at": repo.get("updated_at"),
            }
        )

    return {"query": query, "count": len(items), "repositories": items}


@mcp.tool()
async def get_repository(owner: str, repo: str) -> dict[str, Any]:
    """
    Get metadata for a GitHub repository.

    Args:
        owner: Repository owner or organization.
        repo: Repository name.

    Returns:
        Repository details such as description, stars, language, topics, and visibility.
    """
    data = await _github_request(f"/repos/{owner}/{repo}")
    if "error" in data:
        return data

    return {
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "private": data.get("private"),
        "default_branch": data.get("default_branch"),
        "language": data.get("language"),
        "topics": data.get("topics", []),
        "stars": data.get("stargazers_count"),
        "watchers": data.get("subscribers_count"),
        "forks": data.get("forks_count"),
        "open_issues": data.get("open_issues_count"),
        "license": (data.get("license") or {}).get("spdx_id"),
        "url": data.get("html_url"),
        "clone_url": data.get("clone_url"),
        "updated_at": data.get("updated_at"),
    }


@mcp.tool()
async def list_repository_issues(owner: str, repo: str, state: str = "open", limit: int = 10) -> dict[str, Any]:
    """
    List issues for a repository.

    Args:
        owner: Repository owner or organization.
        repo: Repository name.
        state: Issue state - "open", "closed", or "all".
        limit: Maximum number of issues to return (1-20).

    Returns:
        Repository issues excluding pull requests.
    """
    limit = max(1, min(limit, MAX_ITEMS))
    data = await _github_request(
        f"/repos/{owner}/{repo}/issues",
        params={"state": state, "per_page": limit},
    )
    if isinstance(data, dict) and "error" in data:
        return data

    issues = []
    for item in data:
        if "pull_request" in item:
            continue
        issues.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": item.get("state"),
                "author": (item.get("user") or {}).get("login"),
                "labels": [label.get("name") for label in item.get("labels", [])],
                "comments": item.get("comments"),
                "created_at": item.get("created_at"),
                "url": item.get("html_url"),
            }
        )

    return {"repository": f"{owner}/{repo}", "count": len(issues), "issues": issues}


@mcp.tool()
async def get_issue(owner: str, repo: str, issue_number: int) -> dict[str, Any]:
    """
    Get full details for a specific repository issue.

    Args:
        owner: Repository owner or organization.
        repo: Repository name.
        issue_number: Numeric GitHub issue number.

    Returns:
        Issue metadata and body text.
    """
    data = await _github_request(f"/repos/{owner}/{repo}/issues/{issue_number}")
    if "error" in data:
        return data

    if "pull_request" in data:
        return {"error": "Requested item is a pull request, not a standard issue."}

    return {
        "repository": f"{owner}/{repo}",
        "number": data.get("number"),
        "title": data.get("title"),
        "state": data.get("state"),
        "author": (data.get("user") or {}).get("login"),
        "labels": [label.get("name") for label in data.get("labels", [])],
        "comments": data.get("comments"),
        "body": data.get("body"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at"),
        "url": data.get("html_url"),
    }


@mcp.tool()
async def list_pull_requests(owner: str, repo: str, state: str = "open", limit: int = 10) -> dict[str, Any]:
    """
    List pull requests for a repository.

    Args:
        owner: Repository owner or organization.
        repo: Repository name.
        state: Pull request state - "open", "closed", or "all".
        limit: Maximum number of pull requests to return (1-20).

    Returns:
        Pull request summaries.
    """
    limit = max(1, min(limit, MAX_ITEMS))
    data = await _github_request(
        f"/repos/{owner}/{repo}/pulls",
        params={"state": state, "per_page": limit},
    )
    if isinstance(data, dict) and "error" in data:
        return data

    pulls = []
    for item in data:
        pulls.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": item.get("state"),
                "author": (item.get("user") or {}).get("login"),
                "draft": item.get("draft"),
                "created_at": item.get("created_at"),
                "url": item.get("html_url"),
            }
        )

    return {"repository": f"{owner}/{repo}", "count": len(pulls), "pull_requests": pulls}


@mcp.tool()
async def get_file_content(owner: str, repo: str, path: str, ref: str = "") -> dict[str, Any]:
    """
    Get text file contents from a GitHub repository.

    Args:
        owner: Repository owner or organization.
        repo: Repository name.
        path: File path inside the repository.
        ref: Optional branch, tag, or commit SHA. Uses default branch if omitted.

    Returns:
        Decoded file contents for text files, truncated for safety if large.
    """
    params = {"ref": ref} if ref else None
    data = await _github_request(f"/repos/{owner}/{repo}/contents/{path}", params=params)
    if "error" in data:
        return data

    if data.get("type") != "file":
        return {"error": "Requested path is not a file."}

    encoded_content = data.get("content", "")
    encoding = data.get("encoding")
    if encoding != "base64":
        return {"error": f"Unsupported GitHub content encoding: {encoding}"}

    try:
        decoded = base64.b64decode(encoded_content).decode("utf-8")
    except UnicodeDecodeError:
        return {
            "path": path,
            "repository": f"{owner}/{repo}",
            "size": data.get("size"),
            "error": "File is not UTF-8 text. Binary files are not returned by this example.",
        }

    truncated = False
    if len(decoded) > MAX_FILE_CHARS:
        decoded = decoded[:MAX_FILE_CHARS] + "\n\n... [truncated]"
        truncated = True

    return {
        "repository": f"{owner}/{repo}",
        "path": path,
        "ref": ref or "default branch",
        "size": data.get("size"),
        "truncated": truncated,
        "content": decoded,
        "url": data.get("html_url"),
    }


if __name__ == "__main__":
    print("GitHub Assistant MCP Server")
    print("Tip: set GITHUB_TOKEN for higher rate limits and private repo access.")
    mcp.run()
