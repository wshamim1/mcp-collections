# Claude + MCP Integration

Connect Anthropic's Claude to any MCP server using the Anthropic Python SDK.

## How It Works

```
User Query
    │
    ▼
Claude API ──── given tools from MCP server
    │
    ├── Claude thinks: "I need to call get_weather"
    │
    ▼
MCP Server ──── executes get_weather(city="Tokyo")
    │
    ▼
Result returned to Claude
    │
    ▼
Claude generates final response
```

## Setup

```bash
pip install anthropic mcp
export ANTHROPIC_API_KEY=your-key-here
```

## Run

```bash
cd 06-model-integrations/01-claude
python claude_with_mcp.py
```

## Key Code Pattern

```python
# 1. Load tools from MCP server
tools_result = await session.list_tools()
claude_tools = [mcp_tool_to_claude_format(t) for t in tools_result.tools]

# 2. Send to Claude with tools
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    tools=claude_tools,
    messages=messages,
)

# 3. When Claude calls a tool, route to MCP
if response.stop_reason == "tool_use":
    result = await session.call_tool(tool_name, tool_args)
    # Feed result back to Claude...
```

## Models You Can Use

| Model | Best For |
|-------|----------|
| `claude-3-5-sonnet-20241022` | Best overall (recommended) |
| `claude-3-5-haiku-20241022` | Fast, lightweight tasks |
| `claude-3-opus-20240229` | Most capable, complex reasoning |
