# MCP Resources — Deep Dive

## What Are Resources?

**Resources** expose data to the AI model in a read-only, URI-addressable way. Unlike tools (which the AI calls to *do* things), resources are like a file system or API endpoint that the AI can *read from*.

The AI can browse available resources and fetch their contents on demand.

---

## Resources vs. Tools

| Aspect | Tools | Resources |
|--------|-------|-----------|
| Purpose | Take actions, compute results | Serve data/content |
| AI control | AI decides *when* to call | AI decides *what* to read |
| Side effects | Can have side effects | Read-only |
| Return | Tool result | Text or binary content |
| Schema | Input parameters | URI template pattern |

---

## Resource URI Patterns

```python
# Static resource (fixed URI)
@mcp.resource("config://app/settings")
def get_settings() -> str: ...

# Dynamic resource (URI template)
@mcp.resource("file://{path}")
def read_file(path: str) -> str: ...

# Multi-segment template
@mcp.resource("db://{database}/{table}/{id}")
def get_record(database: str, table: str, id: str) -> str: ...
```

---

## Files in This Section

- `resources_basic.py` — Static and dynamic resource patterns
- `resources_advanced.py` — Directory listing, subscriptions, binary resources

---

## Run the Examples

```bash
mcp dev resources_basic.py
```
