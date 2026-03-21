# Data Analyst — Complete Example

A full end-to-end MCP application combining a SQLite database with AI-powered natural language analysis.

## What It Does

Ask natural language questions about sales data. The AI automatically:
1. Understands the question
2. Writes and executes SQL queries via MCP
3. Analyzes the results
4. Returns insights in plain English

## Try It

```bash
cd examples/data-analyst

# With Claude (recommended)
export ANTHROPIC_API_KEY=your-key
python data_analyst.py

# With local Ollama (no API key needed)
ollama pull llama3.2
python data_analyst.py --model ollama

# Explore with MCP inspector
mcp dev data_analyst.py --server
```

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
