# Database MCP Server

An MCP server providing safe, parameterized access to a SQLite database.

## Features

- `execute_query` — Run SELECT queries (read-only endpoint)
- `execute_write` — Run INSERT/UPDATE/DELETE (configurable)
- `list_tables` — Browse all tables with schemas
- `describe_table` — Schema + sample data for any table
- Auto-creates a demo database with sample data on first run

## Demo Database Schema

```
users        — id, name, email, age, created_at
products     — id, name, price, category, stock
orders       — id, user_id, product_id, quantity, total, ordered_at
```

## Run It

### Option 1: Inspector (Recommended for Testing)
```bash
cd 04-intermediate/02-database-server
mcp dev database_server.py
```

The `mcp dev` command will:
1. Install the MCP Inspector (npm) if needed
2. Start a proxy server on `localhost:6277`
3. Create a demo database with sample sales data
4. Open the interactive inspector in your browser
5. Display all database tools and resources

In the inspector:
- Browse available tables
- Test SQL queries
- See how parameterized queries work
- View resources (table schemas, data)
- Explore database capabilities
- Stop with `Ctrl+C`

### Option 2: Start as Server (Integration)
```bash
cd 04-intermediate/02-database-server
python database_server.py

# Custom database path:
DB_PATH=/path/to/mydb.sqlite python database_server.py

# Read-only mode:
READ_ONLY=true python database_server.py
```

This starts the server on stdio transport, ready for a client like Claude Desktop to connect.

## Example Queries to Ask the AI

- "Show me all users older than 25"
- "What products are in the Electronics category?"
- "Find all orders with their user's name"
- "What's the total revenue from orders?"
- "Add a new user named 'Eve' with email eve@example.com"

## Security

- All queries use parameterized inputs (no SQL injection possible)
- `execute_query` only accepts SELECT/WITH statements
- `execute_write` blocks DROP, TRUNCATE, ALTER, PRAGMA
- Table name validation prevents injection via identifiers
