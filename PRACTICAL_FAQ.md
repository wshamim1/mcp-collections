# Practical FAQ

## 1. Can I build an MCP server for my company database?

Yes. This is one of the best MCP use cases. Keep your database private, and expose only approved business tools like:

- `get_customer_summary(customer_id)`
- `list_open_invoices(account_id)`
- `get_sales_dashboard(region, month)`

This gives consumers useful access without giving direct DB credentials.

## 2. Does MCP mean only big companies host servers?

No. You can run:

- Local MCP servers (for development, internal workflows, personal tools)
- Team/internal servers (behind VPN/private network)
- Public SaaS MCP servers (company-hosted, multi-tenant)

## 3. How do clients use my server?

Typical flow:

1. Client connects to your MCP endpoint
2. Client calls `tools/list`, `resources/list`, `prompts/list`
3. Model chooses what to call based on user request
4. Your server executes and returns structured results

## 4. Why not just expose raw SQL/API access?

MCP gives stronger control:

- Centralized auth and authorization
- Input validation and query guardrails
- Audit logging for every tool call
- Versioned interface for safer evolution

## 5. What should I secure before production?

At minimum:

- Authentication (OAuth/API keys/JWT)
- Authorization (role- and tenant-based)
- Parameterized queries (no SQL injection)
- Rate limits and timeout limits
- Structured logs + monitoring
- TLS for network transport
