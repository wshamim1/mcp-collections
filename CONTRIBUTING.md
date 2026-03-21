# Contributing to MCP Collections

Thank you for your interest in contributing! This repo is designed as a learning resource.

## What to Contribute

- New MCP server examples (e.g., Notion, Slack, GitHub integrations)
- Additional model integrations (Gemini, Cohere, Together AI)
- Improved explanations and diagrams
- Bug fixes in existing examples
- Tests for existing servers

## Getting Started

```bash
# Fork and clone the repo
git clone https://github.com/YOUR_USERNAME/mcp-collections.git
cd mcp-collections

# Set up environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create your feature branch
git checkout -b feature/my-new-server
```

## Code Standards

- Python 3.11+ syntax
- Type hints on all function parameters and return types
- Docstrings on all tools (they appear to the AI!)
- Security by default: validate inputs, sandbox file ops, parameterize queries
- Async tools for anything I/O-bound

## Pull Request Guidelines

1. One example/fix per PR
2. Include a `README.md` in any new directory
3. Add your example to the main `README.md` structure
4. Test with `mcp dev your_server.py`
5. No hardcoded API keys or credentials

## License

By contributing, you agree your contributions are licensed under the MIT License.
