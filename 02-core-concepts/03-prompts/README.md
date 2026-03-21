# MCP Prompts — Deep Dive

## What Are Prompts?

**Prompts** are pre-defined, reusable message templates that users can invoke by name. They parameterize complex instructions so users get consistent, high-quality results without writing long prompts manually.

Prompts differ from tools and resources:
- Tools → AI calls them (autonomous)
- Resources → AI reads data from them
- Prompts → **Users** invoke them to start a conversation

---

## When to Use Prompts

- Complex tasks that need specific instructions (code review, translation)
- Consistent behaviors across different conversations
- Exposing best-practice prompts to non-technical users
- Workflow templates (report generation, analysis, etc.)

---

## Anatomy of a Prompt

```python
from mcp.server.fastmcp import FastMCP
from mcp.types import Message, UserMessage, TextContent

mcp = FastMCP("prompts-demo")

@mcp.prompt()
def code_review(language: str, code: str) -> list[Message]:
    """Review code and provide detailed feedback."""
    return [
        UserMessage(
            TextContent(
                type="text",
                text=f"Please review this {language} code:\n\n```{language}\n{code}\n```\n\n"
                     "Provide feedback on: correctness, style, performance, and security."
            )
        )
    ]
```

---

## Files in This Section

- `prompts_basic.py` — Common prompt patterns

---

## Run the Examples

```bash
mcp dev prompts_basic.py
```
