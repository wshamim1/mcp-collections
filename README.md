# MCP Collections — From Basics to Advanced

> **Model Context Protocol (MCP)** — A complete learning guide with practical Python examples, architecture diagrams, and model integrations.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-1.0+-green.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What is MCP?

**Model Context Protocol (MCP)** is an open standard by Anthropic that enables AI models (like Claude, GPT-4, Ollama, etc.) to securely connect to external tools, data sources, and services through a standardized interface.

Think of MCP as a **universal connector** between AI models and the world — similar to how USB standardizes device connections.

```
Your AI Model  ←——MCP Protocol——→  Tools / Data / Services
```

---

## Repository Structure

```
mcp-collections/
│
├── 01-basics/                    # Start here — fundamentals
│   ├── 01-what-is-mcp/           # Concepts, terminology, overview
│   ├── 02-installation/          # Setup & environment
│   └── 03-first-mcp-server/      # Your first MCP server
│
├── 02-core-concepts/             # Deep dive into MCP primitives
│   ├── 01-tools/                 # Callable functions exposed to models
│   ├── 02-resources/             # Data/files the model can read
│   ├── 03-prompts/               # Reusable prompt templates
│   └── 04-sampling/              # Model sampling through MCP
│
├── 03-architecture/              # How MCP fits together
│   ├── client-server/            # Client-server patterns
│   ├── transport-layers/         # stdio, SSE, WebSocket transports
│   └── security/                 # Auth, sandboxing, trust model
│
├── 04-intermediate/              # Practical real-world servers
│   ├── 01-filesystem-server/     # File operations server
│   ├── 02-database-server/       # SQLite/PostgreSQL server
│   ├── 03-rest-api-server/       # HTTP/REST API wrapper
│   └── 04-weather-server/        # External API integration
│
├── 05-advanced/                  # Production-grade patterns
│   ├── 01-multi-server/          # Orchestrating multiple MCP servers
│   ├── 02-authentication/        # OAuth, API keys, JWT
│   ├── 03-streaming/             # Streaming responses
│   └── 04-production-patterns/   # Logging, error handling, monitoring
│
├── 06-model-integrations/        # Connect different AI models
│   ├── 01-claude/                # Anthropic Claude + MCP
│   ├── 02-openai/                # OpenAI GPT + MCP
│   ├── 03-ollama/                # Local models via Ollama
│   └── 04-multi-model/           # Model switching & routing
│
└── examples/                     # Complete, runnable projects
    ├── todo-manager/             # Full CRUD app with MCP
    ├── code-reviewer/            # AI code review tool
    ├── data-analyst/             # Data analysis assistant
    └── research-assistant/       # Web research + summarization
```

---

## Learning Path

### Beginner (Week 1)
1. [What is MCP?](01-basics/01-what-is-mcp/README.md)
2. [Installation & Setup](01-basics/02-installation/README.md)
3. [Your First MCP Server](01-basics/03-first-mcp-server/README.md)
4. [Understanding Tools](02-core-concepts/01-tools/README.md)
5. [Understanding Resources](02-core-concepts/02-resources/README.md)

### Intermediate (Week 2–3)
6. [Prompts & Templates](02-core-concepts/03-prompts/README.md)
7. [MCP Architecture](03-architecture/README.md)
8. [Filesystem Server](04-intermediate/01-filesystem-server/README.md)
9. [Database Server](04-intermediate/02-database-server/README.md)
10. [REST API Wrapper](04-intermediate/03-rest-api-server/README.md)

### Advanced (Week 4+)
11. [Multi-Server Orchestration](05-advanced/01-multi-server/README.md)
12. [Authentication & Security](05-advanced/02-authentication/README.md)
13. [Streaming with MCP](05-advanced/03-streaming/README.md)
14. [Claude Integration](06-model-integrations/01-claude/README.md)
15. [Multi-Model Routing](06-model-integrations/04-multi-model/README.md)

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/mcp-collections.git
cd mcp-collections

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install base dependencies
pip install mcp

# 4. Run your first MCP server
cd 01-basics/03-first-mcp-server
python simple_server.py
```

---

## Prerequisites

- Python 3.11+
- Basic understanding of async/await in Python
- Familiarity with REST APIs (helpful but not required)

---

## Key Concepts at a Glance

| Concept | Description |
|--------|-------------|
| **Server** | A process that exposes tools/resources via MCP |
| **Client** | An AI model or application that connects to MCP servers |
| **Tool** | A callable function (e.g., `search_web`, `read_file`) |
| **Resource** | Read-only data the model can access (e.g., files, DB records) |
| **Prompt** | Pre-defined prompt templates with dynamic arguments |
| **Transport** | How client/server communicate (stdio, SSE, WebSocket) |

---

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT — see [LICENSE](LICENSE)
