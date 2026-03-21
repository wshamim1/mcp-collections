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

### Option 1: Direct Python (Minimal)
```bash
cd 01-basics/03-first-mcp-server
python simple_server.py
```
This runs the server on stdio transport, waiting for a client to connect.

### Option 2: MCP Inspector (Recommended for Testing)
```bash
mcp dev simple_server.py
```

The `mcp dev` command automates testing and will:

1. **Download the MCP Inspector** if needed
   ```
   Need to install the following packages:
   @modelcontextprotocol/inspector@0.21.1
   Ok to proceed? (y)
   ```
   Answer `y` to proceed with npm package installation.

2. **Start a local proxy server** on `localhost:6277`
   ```
   ⚙️ Proxy server listening on localhost:6277
   🔑 Session token: f3fcc4c48716929779...
   ```

3. **Open the MCP Inspector in your browser** automatically
   ```
   🌐 Opening browser...
   🚀 MCP Inspector is up and running at:
      http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=...
   ```

4. **Display server info** in the inspector UI
   - Shows all available tools
   - Lets you test tools interactively
   - Displays tool inputs/outputs in real-time

Once running, you can:
- Click any tool to test it
- Enter parameters and see results
- View the full request/response JSON-RPC messages
- Stop with `Ctrl+C`

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
