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

### Option 1: Inspector (Recommended for Testing)
```bash
cd examples/research-assistant
mcp dev research_assistant.py
```

The `mcp dev` command will:
1. Install the MCP Inspector (npm) if needed
2. Start a proxy server on `localhost:6277`
3. Open the interactive inspector in your browser
4. Display all available tools

In the inspector:
- Test each research tool individually
- See what parameters they accept
- View results in real-time
- Examine tool schemas
- Stop with `Ctrl+C`

### Option 2: Start as Server (Integration)
```bash
cd examples/research-assistant
python research_assistant.py
```

This starts the server on stdio transport, ready for a client like Claude Desktop to connect.

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
