# Model Integrations

Connect MCP servers to any AI model. Same server, many models.

## Overview

```
                    ┌─── Claude (Anthropic) ───┐
                    │                           │
MCP Server ─────────┼─── GPT-4o (OpenAI) ──────┼──→ User
                    │                           │
                    └─── Llama (Ollama/local) ──┘
```

One MCP server works seamlessly with all models — because the tool calling interface is universal.

## Modules

| Module | Model | Cost | Notes |
|--------|-------|------|-------|
| [01-claude](01-claude/) | Claude 3.5 Sonnet | ~$3/1M input tokens | Best tool use, recommended |
| [02-openai](02-openai/) | GPT-4o | ~$2.5/1M input | Great alternative |
| [03-ollama](03-ollama/) | Llama, Mistral, Qwen | Free | 100% local, private |
| [04-multi-model](04-multi-model/) | Any | Varies | Smart routing between models |

## Quick Comparison

### Claude
```python
# Claude natively supports MCP — straightforward integration
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    tools=claude_tools,   # passed directly from MCP
    messages=messages,
)
```

### OpenAI GPT
```python
# OpenAI uses "function calling" — same concept, slightly different format
response = await client.chat.completions.create(
    model="gpt-4o",
    tools=openai_tools,   # converted from MCP format
    messages=messages,
)
```

### Ollama (Local)
```python
# Ollama mirrors OpenAI's API — works with same tool format
response = await httpx_client.post(
    "http://localhost:11434/api/chat",
    json={"model": "llama3.2", "tools": tools, "messages": messages}
)
```

## Setup

```bash
# Claude
export ANTHROPIC_API_KEY=sk-ant-...

# OpenAI  
export OPENAI_API_KEY=sk-proj-...

# Ollama (local — no API key)
brew install ollama          # macOS
ollama serve                 # start server
ollama pull llama3.2         # download model
```

## Multi-Model Router

The `04-multi-model/multi_model_router.py` implements smart model selection:

- **Availability routing** — Use Claude if key exists, fall back to OpenAI, then Ollama
- **Task-based routing** — Complex reasoning → best model, simple queries → fastest/cheapest
- **Cost-based routing** — Always use cheapest available option
