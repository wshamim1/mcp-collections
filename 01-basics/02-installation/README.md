# Installation & Setup

## Prerequisites

- **Python 3.11+** (3.12 recommended)
- **pip** or **uv** package manager
- A terminal / shell

---

## 1. Verify Python Version

```bash
python --version
# Should output: Python 3.11.x or higher

python -m pip --version
# Should output: pip 23.x or higher
```

---

## 2. Create a Virtual Environment

```bash
# Create the environment
python -m venv .venv

# Activate it
# macOS / Linux:
source .venv/bin/activate

# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Confirm activation (you should see (.venv) in prompt)
which python  # should point to .venv/bin/python
```

---

## 3. Install the MCP SDK

```bash
# Core MCP SDK
pip install mcp

# With CLI tools (recommended for development)
pip install "mcp[cli]"
```

### Using `uv` (faster alternative)

```bash
# Install uv if not already installed
pip install uv

# Create project with uv
uv init my-mcp-project
cd my-mcp-project

# Add MCP dependency
uv add "mcp[cli]"
```

---

## 4. Verify Installation

```bash
python -c "import mcp; print(mcp.__version__)"
# Should print the MCP version

# Check CLI tool
mcp --help
```

---

## 5. Install Development Dependencies

For following along with all examples in this repo:

```bash
pip install \
    mcp \
    anthropic \
    openai \
    httpx \
    aiohttp \
    aiosqlite \
    pydantic \
    python-dotenv \
    rich \
    typer
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

---

## 6. Environment Variables Setup

Create a `.env` file in your project root:

```bash
# .env
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
OLLAMA_BASE_URL=http://localhost:11434
```

Load it in Python:

```python
from dotenv import load_dotenv
import os

load_dotenv()

anthropic_key = os.getenv("ANTHROPIC_API_KEY")
```

---

## 7. Install Claude Desktop (Optional — for testing)

Claude Desktop can connect to local MCP servers directly.

1. Download from: https://claude.ai/download
2. Install and sign in
3. Go to **Settings → Developer → Edit Config**
4. Add your MCP server config:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/path/to/your/server.py"]
    }
  }
}
```

---

## 8. VS Code Setup (Optional)

Install the MCP extension for VS Code:

```bash
# Via CLI
code --install-extension anthropic.mcp
```

---

## 9. Common Ways to Run or Access MCP Servers

There are a few common patterns for accessing MCP servers, depending on how the server is distributed.

### Option A: Run a local Python file directly

Best when you have the server source code locally.

```bash
python server.py

# Or inspect it interactively
mcp dev server.py
```

### Option B: Run using `uv`

Useful when the project uses `pyproject.toml` and you want reproducible local execution.

```bash
uv run server.py

# Or with dependencies resolved via uv
uv run --with mcp python server.py
```

This is also what you may see under the hood when Inspector launches a local file-based server.

### Option C: Run a packaged server installed with `pip`

Some MCP servers are published as Python packages.

```bash
pip install my-mcp-server

# Then run the package's CLI entry point
my-mcp-server
```

Or if the package exposes a module entrypoint:

```bash
python -m my_mcp_server
```

### Option D: Run using `uvx`

`uvx` is useful when you want to run a published tool without permanently installing it into your environment.

```bash
uvx my-mcp-server
```

This is similar to `npx` in the Node.js ecosystem.

Good for:

- quick evaluation of a public MCP server
- trying a server without modifying your current environment
- running a packaged tool in CI or disposable environments

### Option E: Connect to a remote hosted MCP server

If a company hosts an MCP server remotely, you do not run the source code locally. Instead, your client connects to the hosted endpoint.

Typical pattern:

- internal server over VPN/private network
- external hosted server over SSE/HTTP
- authentication via API key, OAuth, or gateway token

In this case, the client discovers tools/resources/prompts from the remote server rather than launching a local process.

### Claude Desktop / client config examples

**Local Python file**

```json
{
  "mcpServers": {
    "my-local-server": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

**Using `uv`**

```json
{
  "mcpServers": {
    "my-uv-server": {
      "command": "uv",
      "args": ["run", "/absolute/path/to/server.py"]
    }
  }
}
```

**Using an installed CLI**

```json
{
  "mcpServers": {
    "my-packaged-server": {
      "command": "my-mcp-server",
      "args": []
    }
  }
}
```

### Which option should I choose?

- Use `python server.py` when developing locally
- Use `mcp dev server.py` when testing interactively
- Use `uv run` when your project is managed with `uv`
- Use `uvx` when evaluating public packaged servers quickly
- Use `pip install` when you want a stable installed CLI
- Use remote SSE/HTTP when the server is hosted by another team or company

---

## Project Structure for MCP Development

```
my-mcp-project/
├── .env                    # API keys (never commit this!)
├── .gitignore
├── requirements.txt
├── pyproject.toml          # If using uv/poetry
│
├── server.py               # Your MCP server
├── client.py               # Test client
│
└── tools/                  # Modular tools
    ├── __init__.py
    ├── web_tools.py
    └── file_tools.py
```

---

## Recommended `.gitignore`

```gitignore
.env
.venv/
__pycache__/
*.pyc
*.egg-info/
dist/
.DS_Store
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'mcp'`
Ensure your virtual environment is activated:
```bash
source .venv/bin/activate
pip install mcp
```

### `python: command not found`
Use `python3` on macOS/Linux:
```bash
python3 -m venv .venv
python3 -m pip install mcp
```

### MCP version conflicts
```bash
pip install --upgrade mcp
pip show mcp  # Check installed version
```

---

## Next Steps

- [Your First MCP Server →](../03-first-mcp-server/README.md)
