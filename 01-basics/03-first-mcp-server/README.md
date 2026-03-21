# Your First MCP Server

This tutorial builds a simple MCP server step by step, explaining every part.

---

## What We're Building

A basic MCP server with 3 tools:
- `greet` — returns a greeting message
- `add_numbers` — adds two numbers together
- `get_time` — returns the current time

---

## The Code

```
03-first-mcp-server/
├── simple_server.py      # The MCP server
├── test_client.py        # Test it manually
└── README.md
```

---

## Run It

```bash
cd 01-basics/03-first-mcp-server
python simple_server.py
```

To test with the MCP inspector:
```bash
mcp dev simple_server.py
```

---

## Key Concepts Demonstrated

1. **`FastMCP`** — high-level server class (simplest way to build)
2. **`@mcp.tool()`** — decorator to expose a Python function as a tool
3. **Type hints** — automatically generate JSON schemas for the AI
4. **Docstrings** — become the tool description the AI reads
5. **`mcp.run()`** — start the server using stdio transport

---

## Next Steps

- [Understanding Tools →](../../02-core-concepts/01-tools/README.md)
- [Understanding Resources →](../../02-core-concepts/02-resources/README.md)
