# GitHub Assistant — Complete Example

A practical MCP server that wraps common GitHub workflows for repositories, issues, pull requests, and files.

## What It Does

This example exposes read-only GitHub operations as MCP tools so an AI client can:

- search repositories
- inspect repository metadata
- review issues and pull requests
- fetch issue details
- read repository files such as `README.md`, config files, or source files

## Tools

| Tool | Description |
|---|---|
| `search_repositories` | Search public GitHub repositories by keyword |
| `get_repository` | Get repository metadata and statistics |
| `list_repository_issues` | List repository issues |
| `get_issue` | Read one issue in detail |
| `list_pull_requests` | List repository pull requests |
| `get_file_content` | Read a text file from a repository |

## Setup

Optional but recommended:

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

Why use a token:
- higher GitHub API rate limits
- access to private repositories the token can read
- more reliable testing during development

If you do not set `GITHUB_TOKEN`, the example still works for public repositories, but unauthenticated GitHub API rate limits are much lower.

## Run It

### Option 1: Inspector (Recommended for Testing)
```bash
cd examples/github-assistant
mcp dev github_assistant.py
```

In the inspector you can:
- search for repositories like `mcp python`
- inspect `anthropics/anthropic-sdk-python`-style public repos
- read `README.md` or config files
- review issues and pull requests

### Option 2: Start as Server (Integration)
```bash
cd examples/github-assistant
python github_assistant.py
```

This starts the server on stdio transport, ready for a client like Claude Desktop to connect.

## Example Prompt Ideas

- "Find popular Python repositories about MCP"
- "Show open issues for owner/repo"
- "Read the README.md from a repository and summarize it"
- "List recent pull requests in this repository"
- "Inspect issue 123 in owner/repo and summarize the problem"

## Notes

- This example is intentionally read-only
- It is safe as a starting point for enterprise GitHub MCP design
- You can extend it later with write tools like commenting on issues or creating pull requests, but those should require stronger auth and audit controls
