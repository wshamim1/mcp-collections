# MCP Tools — Deep Dive

## What Are Tools?

**Tools** are Python functions that you expose to an AI model so it can call them autonomously. The AI decides *when* and *how* to use them based on user intent.

Think of tools like the AI's "hands" — a way to take actions in the world.

---

## Anatomy of a Tool

```python
@mcp.tool()
def tool_name(param1: type, param2: type = default) -> return_type:
    """
    Short description (required — AI reads this to decide when to use tool).

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of the return value.
    """
    # implementation
    return result
```

**What MCP does automatically:**
- Reads type hints → generates JSON Schema for validation
- Reads docstring → creates tool description shown to the AI
- Handles serialization/deserialization of inputs & outputs

---

## Tool Return Types

Tools can return multiple types — MCP handles them all:

| Return Type | MCP Content Type | Example |
|-------------|-----------------|---------|
| `str` | TextContent | `"Hello world"` |
| `dict` / `list` | TextContent (JSON) | `{"result": 42}` |
| `bytes` / blob | BlobContent | Binary file data |
| `Image` | ImageContent | Screenshots, charts |

---

## Files in This Section

- `tools_basic.py` — Simple tool patterns
- `tools_advanced.py` — Complex inputs, error handling, async tools
- `tools_with_context.py` — Using MCP context in tools

---

## Run the Examples

```bash
# Test basic tools
mcp dev tools_basic.py

# Test advanced tools
mcp dev tools_advanced.py
```
