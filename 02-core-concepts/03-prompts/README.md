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

mcp = FastMCP("prompts-demo")

@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """Review code and provide detailed feedback."""
    return (
        f"Please review this {language} code:\n\n```{language}\n{code}\n```\n\n"
        "Provide feedback on: correctness, style, performance, and security."
    )
```

---

## Files in This Section

- `prompts_basic.py` — Common prompt patterns

---

## Run the Examples

```bash
mcp dev prompts_basic.py
```

The `mcp dev` command will:
1. Install the MCP Inspector (npm) if needed
2. Start a proxy server on `localhost:6277`
3. Open the interactive inspector in your browser
4. Display all available prompts

In the inspector:
- Browse all prompt templates
- See prompt arguments and descriptions
- Understand when to use each prompt
- View prompt structure
- Stop with `Ctrl+C`

### Example Prompt Inputs

Some prompts require arguments before they can run in the inspector.

**`translate_text`**
- Required: `text`, `target_language`
- Optional: `formality` (defaults to `neutral`)

Example values:

```json
{
    "text": "Hello, how are you today?",
    "target_language": "Spanish",
    "formality": "formal"
}
```

**`code_review`**

```json
{
    "language": "python",
    "code": "def add(a, b):\n    return a + b"
}
```
