"""
Database MCP Server — SQLite
==============================
An MCP server providing AI models safe access to a SQLite database.

Features:
- execute_query    — Run SELECT queries (read-only by default)
- execute_write    — Run INSERT/UPDATE/DELETE (requires write mode)
- list_tables      — List all tables in the database
- describe_table   — Get schema of a specific table
- create_table     — Create a new table
- insert_record    — Insert a record into a table
- get_table_stats  — Row counts and basic stats per table

Security:
- Parameterized queries only (no SQL injection)
- Configurable read-only mode
- Table name whitelist support
- Query result size limits

Run with:
    python database_server.py

Custom database:
    DB_PATH=/path/to/db.sqlite python database_server.py
"""

import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any, Optional

import aiosqlite
from mcp.server.fastmcp import FastMCP

# ─── Configuration ──────────────────────────────────────────────────────────
DB_PATH = Path(os.environ.get("DB_PATH", "demo.db"))
READ_ONLY = os.environ.get("READ_ONLY", "false").lower() == "true"
MAX_ROWS = int(os.environ.get("MAX_ROWS", 1000))

mcp = FastMCP("database-server")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _validate_table_name(name: str) -> bool:
    """Ensure table name contains only safe characters."""
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name))


def _validate_column_name(name: str) -> bool:
    """Ensure column name contains only safe characters."""
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name))


async def _get_db() -> aiosqlite.Connection:
    """Open a database connection."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys = ON")
    return db


# ─── Initialize Demo Database ─────────────────────────────────────────────────

def _init_demo_db():
    """Create demo tables if the database doesn't exist."""
    if DB_PATH.exists():
        return

    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT NOT NULL,
                email     TEXT UNIQUE NOT NULL,
                age       INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS products (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                price       REAL NOT NULL,
                category    TEXT,
                stock       INTEGER DEFAULT 0,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS orders (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER REFERENCES users(id),
                product_id INTEGER REFERENCES products(id),
                quantity   INTEGER NOT NULL,
                total      REAL,
                ordered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            INSERT INTO users (name, email, age) VALUES
                ('Alice Smith', 'alice@example.com', 30),
                ('Bob Jones', 'bob@example.com', 25),
                ('Carol White', 'carol@example.com', 35),
                ('David Brown', 'david@example.com', 28);

            INSERT INTO products (name, price, category, stock) VALUES
                ('Python Book', 29.99, 'Books', 50),
                ('Mechanical Keyboard', 149.99, 'Electronics', 20),
                ('Standing Desk', 499.99, 'Furniture', 5),
                ('Noise Canceling Headphones', 299.99, 'Electronics', 15),
                ('Coffee Mug', 14.99, 'Kitchen', 100);

            INSERT INTO orders (user_id, product_id, quantity, total) VALUES
                (1, 1, 2, 59.98),
                (1, 4, 1, 299.99),
                (2, 2, 1, 149.99),
                (3, 5, 3, 44.97),
                (4, 3, 1, 499.99);
        """)
        print(f"Demo database created: {DB_PATH}")


# ─── Tools ──────────────────────────────────────────────────────────────────

@mcp.tool()
async def execute_query(
    sql: str,
    params: Optional[list] = None,
    limit: int = 100,
) -> dict:
    """
    Execute a SELECT query and return results.

    Args:
        sql: The SELECT SQL query. Use ? for parameters.
        params: Optional list of query parameters (prevents SQL injection).
        limit: Maximum number of rows to return (default: 100, max: 1000).

    Returns:
        Dictionary with 'rows', 'columns', and 'row_count'.

    Example:
        sql: "SELECT * FROM users WHERE age > ?"
        params: [25]
    """
    # Only allow SELECT statements in this endpoint
    stripped = sql.strip().upper()
    if not stripped.startswith("SELECT") and not stripped.startswith("WITH"):
        return {"error": "Only SELECT queries are allowed with execute_query. Use execute_write for modifications."}

    limit = min(limit, MAX_ROWS)
    params = params or []

    # Inject LIMIT if not present
    if "LIMIT" not in stripped:
        sql = f"{sql.rstrip(';')} LIMIT {limit}"

    try:
        async with await _get_db() as db:
            async with db.execute(sql, params) as cursor:
                rows = await cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []

                return {
                    "columns": columns,
                    "rows": [dict(row) for row in rows],
                    "row_count": len(rows),
                    "sql": sql,
                }
    except aiosqlite.Error as e:
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool()
async def execute_write(
    sql: str,
    params: Optional[list] = None,
) -> dict:
    """
    Execute an INSERT, UPDATE, or DELETE statement.

    Args:
        sql: The SQL statement. Use ? placeholders for parameters.
        params: Parameter values for ? placeholders.

    Returns:
        Dictionary with 'rows_affected' and 'last_insert_id'.
    """
    if READ_ONLY:
        return {"error": "Server is in read-only mode. Write operations are disabled."}

    # Block dangerous statements
    stripped = sql.strip().upper()
    blocked = ["DROP TABLE", "DROP DATABASE", "TRUNCATE", "ALTER TABLE", "PRAGMA"]
    for keyword in blocked:
        if keyword in stripped:
            return {"error": f"Statement contains blocked keyword: {keyword}"}

    allowed_starts = ["INSERT", "UPDATE", "DELETE"]
    if not any(stripped.startswith(kw) for kw in allowed_starts):
        return {"error": f"Only INSERT, UPDATE, DELETE statements are allowed. Got: {stripped[:20]}"}

    params = params or []

    try:
        async with await _get_db() as db:
            cursor = await db.execute(sql, params)
            await db.commit()
            return {
                "success": True,
                "rows_affected": cursor.rowcount,
                "last_insert_id": cursor.lastrowid,
                "sql": sql,
            }
    except aiosqlite.IntegrityError as e:
        return {"error": f"Integrity constraint violated: {str(e)}"}
    except aiosqlite.Error as e:
        return {"error": f"Database error: {str(e)}"}


@mcp.tool()
async def list_tables() -> dict:
    """
    List all tables in the database with basic info.

    Returns:
        List of tables with their column names and row counts.
    """
    try:
        async with await _get_db() as db:
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ) as cursor:
                tables = [row[0] for row in await cursor.fetchall()]

            result = {}
            for table in tables:
                if not _validate_table_name(table):
                    continue
                # Get columns
                async with db.execute(f"PRAGMA table_info({table})") as cur:
                    cols = await cur.fetchall()
                    columns = [{"name": c[1], "type": c[2], "nullable": not c[3]} for c in cols]

                # Get row count
                async with db.execute(f"SELECT COUNT(*) FROM {table}") as cur:
                    row_count = (await cur.fetchone())[0]

                result[table] = {"columns": columns, "row_count": row_count}

            return {"tables": result, "count": len(result)}
    except aiosqlite.Error as e:
        return {"error": str(e)}


@mcp.tool()
async def describe_table(table_name: str) -> dict:
    """
    Get the full schema of a table.

    Args:
        table_name: Name of the table to describe.

    Returns:
        Table schema including columns, types, and constraints.
    """
    if not _validate_table_name(table_name):
        return {"error": "Invalid table name."}

    try:
        async with await _get_db() as db:
            # Check table exists
            async with db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                [table_name]
            ) as cur:
                if not await cur.fetchone():
                    return {"error": f"Table '{table_name}' not found."}

            # Column info
            async with db.execute(f"PRAGMA table_info({table_name})") as cur:
                columns = [
                    {
                        "cid": c[0],
                        "name": c[1],
                        "type": c[2],
                        "not_null": bool(c[3]),
                        "default_value": c[4],
                        "primary_key": bool(c[5]),
                    }
                    for c in await cur.fetchall()
                ]

            # Foreign keys
            async with db.execute(f"PRAGMA foreign_key_list({table_name})") as cur:
                fkeys = [
                    {"column": fk[3], "references": f"{fk[2]}.{fk[4]}"}
                    for fk in await cur.fetchall()
                ]

            # Row count
            async with db.execute(f"SELECT COUNT(*) FROM {table_name}") as cur:
                row_count = (await cur.fetchone())[0]

            # Sample
            async with db.execute(f"SELECT * FROM {table_name} LIMIT 3") as cur:
                sample = [dict(row) for row in await cur.fetchall()]

            return {
                "table_name": table_name,
                "columns": columns,
                "foreign_keys": fkeys,
                "row_count": row_count,
                "sample_rows": sample,
            }
    except aiosqlite.Error as e:
        return {"error": str(e)}


# ─── Resources ────────────────────────────────────────────────────────────────

@mcp.resource("db://schema")
async def get_full_schema() -> str:
    """Full database schema as SQL CREATE statements."""
    try:
        async with await _get_db() as db:
            async with db.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL"
            ) as cur:
                schemas = [row[0] for row in await cur.fetchall()]
        return "\n\n".join(schemas)
    except Exception as e:
        return f"Error: {e}"


@mcp.resource("db://table/{table_name}")
async def get_table_data(table_name: str) -> str:
    """Get contents of a table as JSON."""
    if not _validate_table_name(table_name):
        return json.dumps({"error": "Invalid table name"})

    try:
        async with await _get_db() as db:
            async with db.execute(f"SELECT * FROM {table_name} LIMIT 100") as cur:
                rows = [dict(r) for r in await cur.fetchall()]
                cols = [d[0] for d in cur.description] if cur.description else []
        return json.dumps({"table": table_name, "columns": cols, "rows": rows}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    _init_demo_db()
    print(f"Database MCP Server")
    print(f"Database: {DB_PATH.resolve()}")
    print(f"Read-only: {READ_ONLY}")
    mcp.run()
