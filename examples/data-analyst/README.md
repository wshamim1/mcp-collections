# Data Analyst — Complete Example

A full end-to-end MCP application combining a SQLite database with AI-powered natural language analysis.

## What It Does

Ask natural language questions about sales data. The AI automatically:
1. Understands the question
2. Writes and executes SQL queries via MCP
3. Analyzes the results
4. Returns insights in plain English

## Try It

### Option 1: Standalone Analyzer

**With Claude (recommended)**
```bash
cd examples/data-analyst
export ANTHROPIC_API_KEY=your-key
python data_analyst.py
```

This will:
1. Create a demo database with sample sales data
2. Connect to Claude API
3. Run analysis and display insights

**With local Ollama (no API key needed)**
```bash
cd examples/data-analyst
ollama pull llama3.2
python data_analyst.py --model ollama
```

### Option 2: Inspect Tools with MCP Inspector
```bash
cd examples/data-analyst
mcp dev data_analyst.py
```

The `mcp dev` command will:
1. Install the MCP Inspector (npm) if needed
2. Start a proxy server on `localhost:6277`
3. Open the interactive inspector in your browser
4. Display all available analysis tools

In the inspector:
- Test database queries
- See available tables and schemas
- Call analysis tools manually
- View results immediately
- Stop with `Ctrl+C`

## Sample Questions

- "Which product category generates the most revenue?"
- "Who are our top customers?"
- "Show me monthly revenue trends"
- "What's our profit margin by region?"
- "Which products have the best margin?"

## Database Schema

```
products    — Electronics, Furniture, Books, Kitchen items
customers   — 6 customers across North/South/East/West regions
sales       — 15 transactions in 2024 with quantity and discounts
```
