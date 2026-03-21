"""
MCP SSE Transport — Remote Server Example
==========================================
Demonstrates running an MCP server over HTTP using SSE (Server-Sent Events).
This is the pattern for deploying shared, remote MCP servers.

Install extra deps:
    pip install "mcp[cli]" uvicorn

Run the server:
    python sse_server.py

Connect from client:
    Use sse_client("http://localhost:8000/sse") in your MCP client
"""

from datetime import datetime
from mcp.server.fastmcp import FastMCP

# ─── Create server with SSE transport ─────────────────────────────────────────
# host and port configure the HTTP server
mcp = FastMCP(
    "remote-tools-server",
    host="0.0.0.0",   # Accept connections from any interface
    port=8000,
)


@mcp.tool()
def ping() -> dict:
    """Check if the server is running."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "server": "remote-tools-server",
    }


@mcp.tool()
def get_server_info() -> dict:
    """Get information about this MCP server."""
    return {
        "name": "remote-tools-server",
        "transport": "SSE over HTTP",
        "endpoint": "http://localhost:8000/sse",
        "description": "Demonstrates SSE transport for remote MCP servers",
    }


@mcp.tool()
async def echo(message: str) -> str:
    """
    Echo a message back (useful for testing connectivity).

    Args:
        message: The message to echo back.
    """
    return f"Echo: {message}"


@mcp.tool()
def calculate(expression: str) -> dict:
    """
    Safely evaluate a mathematical expression.

    Args:
        expression: A math expression like "2 + 2 * 10" or "sqrt(16)".

    Returns:
        Dictionary with the result or error message.
    """
    import ast
    import math

    # Safe math functions whitelist
    safe_names = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sqrt": math.sqrt, "pow": math.pow, "log": math.log,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "pi": math.pi, "e": math.e,
    }

    try:
        # Parse to AST and validate — no arbitrary code execution
        tree = ast.parse(expression, mode="eval")
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if not (isinstance(node.func, ast.Name) and node.func.id in safe_names):
                    return {"error": "Function not allowed in safe mode"}
            elif isinstance(node, ast.Name):
                if node.id not in safe_names:
                    return {"error": f"Name '{node.id}' not allowed"}

        result = eval(compile(tree, "<string>", "eval"), {"__builtins__": {}}, safe_names)
        return {"expression": expression, "result": result}
    except ZeroDivisionError:
        return {"error": "Division by zero"}
    except Exception as e:
        return {"error": f"Invalid expression: {str(e)}"}


# ─── Run with SSE transport ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Starting SSE MCP server on http://localhost:8000")
    print("Connect clients to: http://localhost:8000/sse")
    # "sse" transport runs an HTTP server with SSE endpoint
    mcp.run(transport="sse")
