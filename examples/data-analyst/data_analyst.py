"""
Complete Example: AI Data Analyst
===================================
A full end-to-end MCP application that combines:
- SQLite database server (data storage)
- Analysis tools (aggregation, statistics)
- Any AI model (Claude/GPT-4o/Ollama)

The user asks natural language questions about data and the AI:
1. Queries the database using MCP tools
2. Performs calculations
3. Returns insights in plain English

Features demonstrated:
- Real database with sample sales data
- SQL queries via MCP
- Statistical analysis tools
- Works with any model (Claude, OpenAI, Ollama)

Setup:
    pip install mcp anthropic aiosqlite
    export ANTHROPIC_API_KEY=your-key   # or OPENAI_API_KEY

Run:
    python data_analyst.py
    python data_analyst.py --model ollama  # local model
"""

import asyncio
import json
import os
import sqlite3
import sys
from pathlib import Path

import aiosqlite
from mcp.server.fastmcp import FastMCP

# ─── Create Sample Database ─────────────────────────────────────────────────

DB_PATH = Path(__file__).parent / "sales.db"


def ensure_database_ready() -> None:
    """Create demo DB if missing so inspector/tool calls always have tables."""
    create_sample_database()


def create_sample_database():
    """Create a realistic sales database for analysis demos."""
    if DB_PATH.exists():
        return

    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                cost REAL NOT NULL
            );

            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                region TEXT NOT NULL,
                joined_date TEXT NOT NULL
            );

            CREATE TABLE sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER REFERENCES products(id),
                customer_id INTEGER REFERENCES customers(id),
                quantity INTEGER NOT NULL,
                sale_date TEXT NOT NULL,
                discount_pct REAL DEFAULT 0
            );

            INSERT INTO products VALUES
                (1, 'Laptop Pro', 'Electronics', 1299.99, 800.00),
                (2, 'Wireless Mouse', 'Electronics', 49.99, 15.00),
                (3, 'USB-C Hub', 'Electronics', 79.99, 25.00),
                (4, 'Standing Desk', 'Furniture', 599.99, 300.00),
                (5, 'Ergonomic Chair', 'Furniture', 449.99, 200.00),
                (6, 'Python Mastery Book', 'Books', 39.99, 8.00),
                (7, 'AI Engineering Book', 'Books', 44.99, 10.00),
                (8, 'Coffee Maker', 'Kitchen', 129.99, 45.00);

            INSERT INTO customers VALUES
                (1, 'Alice Johnson', 'alice@example.com', 'North', '2023-01-15'),
                (2, 'Bob Smith', 'bob@example.com', 'South', '2023-03-20'),
                (3, 'Carol Davis', 'carol@example.com', 'East', '2023-02-10'),
                (4, 'David Wilson', 'david@example.com', 'West', '2023-05-05'),
                (5, 'Eve Martinez', 'eve@example.com', 'North', '2023-06-18'),
                (6, 'Frank Chen', 'frank@example.com', 'East', '2023-07-22');

            INSERT INTO sales (product_id, customer_id, quantity, sale_date, discount_pct) VALUES
                (1, 1, 2, '2024-01-15', 0),
                (2, 1, 3, '2024-01-15', 10),
                (4, 2, 1, '2024-01-20', 5),
                (6, 3, 2, '2024-02-01', 0),
                (7, 3, 1, '2024-02-01', 0),
                (3, 4, 2, '2024-02-14', 15),
                (5, 5, 1, '2024-03-01', 0),
                (8, 6, 1, '2024-03-10', 0),
                (1, 2, 1, '2024-03-15', 10),
                (2, 4, 5, '2024-03-20', 20),
                (6, 5, 3, '2024-04-01', 0),
                (4, 1, 1, '2024-04-10', 0),
                (3, 3, 1, '2024-04-15', 5),
                (7, 6, 2, '2024-05-01', 0),
                (1, 5, 1, '2024-05-20', 0);
        """)
    print(f"✅ Sample database created: {DB_PATH}")


# ─── MCP Analyst Server ───────────────────────────────────────────────────────

mcp = FastMCP("data-analyst-server")


@mcp.tool()
async def query_sales(sql: str) -> dict:
    """
    Run a SELECT query on the sales database.
    Tables: products(id,name,category,price,cost),
            customers(id,name,email,region,joined_date),
            sales(id,product_id,customer_id,quantity,sale_date,discount_pct)

    Args:
        sql: A SELECT query to run.

    Returns:
        Query results with columns and rows.
    """
    if not sql.strip().upper().startswith("SELECT"):
        return {"error": "Only SELECT queries allowed."}

    ensure_database_ready()

    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(sql) as cursor:
                rows = await cursor.fetchall()
                columns = [d[0] for d in cursor.description] if cursor.description else []
                return {
                    "columns": columns,
                    "rows": [dict(r) for r in rows],
                    "count": len(rows),
                }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def calculate_revenue(
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31",
    group_by: str = "month",
) -> dict:
    """
    Calculate revenue for a date range, optionally grouped.

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        group_by: Group results by "month", "category", "region", or "product".
    """
    group_clauses = {
        "month": ("strftime('%Y-%m', s.sale_date)", "period"),
        "category": ("p.category", "category"),
        "region": ("c.region", "region"),
        "product": ("p.name", "product"),
    }

    if group_by not in group_clauses:
        return {"error": f"group_by must be one of: {list(group_clauses.keys())}"}

    ensure_database_ready()

    group_expr, alias = group_clauses[group_by]

    sql = f"""
        SELECT
            {group_expr} AS {alias},
            COUNT(*) AS transactions,
            SUM(s.quantity) AS units_sold,
            ROUND(SUM(s.quantity * p.price * (1 - s.discount_pct/100.0)), 2) AS revenue,
            ROUND(SUM(s.quantity * (p.price - p.cost) * (1 - s.discount_pct/100.0)), 2) AS profit
        FROM sales s
        JOIN products p ON s.product_id = p.id
        JOIN customers c ON s.customer_id = c.id
        WHERE s.sale_date BETWEEN ? AND ?
        GROUP BY {group_expr}
        ORDER BY revenue DESC
    """

    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(sql, [start_date, end_date]) as cursor:
                rows = [dict(r) for r in await cursor.fetchall()]

        total_revenue = sum(r["revenue"] for r in rows)
        total_profit = sum(r["profit"] for r in rows)

        return {
            "period": f"{start_date} to {end_date}",
            "group_by": group_by,
            "data": rows,
            "totals": {
                "revenue": round(total_revenue, 2),
                "profit": round(total_profit, 2),
                "margin_pct": round(total_profit / total_revenue * 100, 1) if total_revenue else 0,
            },
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def top_customers(limit: int = 5) -> dict:
    """
    Get the top customers by total spending.

    Args:
        limit: Number of top customers to return.
    """
    sql = """
        SELECT
            c.name,
            c.region,
            COUNT(DISTINCT s.id) AS orders,
            ROUND(SUM(s.quantity * p.price * (1 - s.discount_pct/100.0)), 2) AS total_spent
        FROM customers c
        JOIN sales s ON c.id = s.customer_id
        JOIN products p ON s.product_id = p.id
        GROUP BY c.id
        ORDER BY total_spent DESC
        LIMIT ?
    """
    ensure_database_ready()
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(sql, [limit]) as cur:
                return {
                    "top_customers": [dict(r) for r in await cur.fetchall()],
                    "limit": limit,
                }
    except Exception as e:
        return {"error": str(e)}


@mcp.resource("db://schema")
def get_schema() -> str:
    """Database schema for the sales analytics database."""
    return """
    products(id, name, category, price, cost)
    customers(id, name, email, region, joined_date)
    sales(id, product_id, customer_id, quantity, sale_date, discount_pct)
    """


# ─── AI Query Runner ────────────────────────────────────────────────────────

async def ask_analyst(question: str, model_provider: str = "auto") -> str:
    """Run the data analyst agent with the specified question."""
    from mcp import StdioServerParameters
    from mcp.client.stdio import stdio_client

    # Import model connector
    if model_provider == "ollama" or (
        model_provider == "auto"
        and not os.environ.get("ANTHROPIC_API_KEY")
        and not os.environ.get("OPENAI_API_KEY")
    ):
        return await _ask_with_ollama(question)
    elif model_provider == "openai" or (
        model_provider == "auto" and not os.environ.get("ANTHROPIC_API_KEY")
    ):
        return await _ask_with_openai(question)
    else:
        return await _ask_with_claude(question)


async def _ask_with_claude(question: str) -> str:
    import anthropic
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    params = StdioServerParameters(command="python", args=[__file__, "--server"])

    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            tools_result = await session.list_tools()

            tools = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema,
                }
                for t in tools_result.tools
            ]

            messages = [
                {
                    "role": "user",
                    "content": f"You are a data analyst. Answer this question using the available tools:\n\n{question}"
                }
            ]

            for _ in range(5):
                resp = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2048,
                    tools=tools,
                    messages=messages,
                )

                if resp.stop_reason == "end_turn":
                    return " ".join(b.text for b in resp.content if hasattr(b, "text"))

                messages.append({"role": "assistant", "content": resp.content})
                tool_results = []

                for block in resp.content:
                    if block.type != "tool_use":
                        continue
                    result = await session.call_tool(block.name, block.input)
                    result_text = " ".join(c.text for c in result.content if hasattr(c, "text"))
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text,
                    })

                messages.append({"role": "user", "content": tool_results})

    return "Analysis complete."


async def _ask_with_openai(question: str) -> str:
    # Similar implementation using OpenAI — see 06-model-integrations/02-openai/
    return "OpenAI integration: see 06-model-integrations/02-openai/openai_with_mcp.py"


async def _ask_with_ollama(question: str) -> str:
    # Similar implementation using Ollama — see 06-model-integrations/03-ollama/
    return "Ollama integration: see 06-model-integrations/03-ollama/ollama_with_mcp.py"


# ─── Entry Point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--server" in sys.argv:
        # Running as MCP server
        create_sample_database()
        mcp.run()
    else:
        # Running as demo application
        create_sample_database()

        print("=" * 55)
        print("  AI DATA ANALYST — COMPLETE EXAMPLE")
        print("=" * 55)

        model = "auto"
        if "--model" in sys.argv:
            idx = sys.argv.index("--model")
            if idx + 1 < len(sys.argv):
                model = sys.argv[idx + 1]

        questions = [
            "Which product category generates the most revenue?",
            "Who are our top 3 customers and how much have they spent?",
            "What are the monthly revenue trends in 2024?",
        ]

        print(f"\nModel: {model}")

        for question in questions[:1]:  # Run one question in demo
            print(f"\n💬 Question: {question}")
            print("🤔 Analyzing...")

            if not os.environ.get("ANTHROPIC_API_KEY") and model == "auto":
                print("\n⚠️  Set ANTHROPIC_API_KEY to use Claude.")
                print("   Or use: python data_analyst.py --model ollama")
                print("\n📊 Starting in server mode instead (test with: mcp dev data_analyst.py)")
                mcp.run()
                break

            response = asyncio.run(ask_analyst(question, model))
            print(f"\n📊 Answer: {response}")
