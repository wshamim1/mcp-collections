# Research Assistant — Complete Example

An AI-powered research assistant that searches Wikipedia, reads web pages, and saves notes.

## Tools

| Tool | Description |
|------|-------------|
| `search_wikipedia` | Search Wikipedia for a topic |
| `get_wikipedia_article` | Get full article content |
| `fetch_webpage_text` | Read any HTTPS webpage |
| `save_research_note` | Save findings as markdown notes |
| `list_research_notes` | Browse saved notes |
| `read_research_note` | Read a specific note |

## Run It

```bash
cd examples/research-assistant

# Explore tools with inspector
mcp dev research_assistant.py

# Start server
python research_assistant.py
```

## Example Prompts to Try

With Claude Desktop or your MCP client connected:

- "Research Model Context Protocol and summarize how it works"
- "Find information about quantum computing and save it as a note"
- "What is LangChain? Compare it with MCP"
- "Research the history of Python and save detailed notes"
- "Find and summarize recent AI model architectures"

## Security Notes

- Only HTTPS URLs allowed (prevents HTTP downgrade)
- SSRF protection: blocks private/internal IP addresses
- Notes sandboxed to `notes/` directory
- Filename sanitization prevents path traversal
