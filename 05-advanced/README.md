# Advanced MCP Topics

## Overview

This section covers production-grade patterns for real-world MCP deployments.

## Modules

### [01-multi-server](01-multi-server/)
Connect a single client to **multiple MCP servers** simultaneously. This is how Claude Desktop works — combining tools from filesystem, database, weather, and custom servers into one unified interface.

**Key concept:** Tool routing — when you have 50+ tools from 10 servers, how does the client know which server handles `query_database` vs `read_file`?

### [02-authentication](02-authentication/)
Secure your MCP servers:
- API key validation (with timing-attack prevention)
- Session tokens
- Role-based access control (admin vs user)
- Environment-variable secret management

### [03-streaming](03-streaming/)
Handle long-running operations:
- Progress notifications during tool execution
- Streaming large responses
- Cancellation support

### [04-production-patterns](04-production-patterns/)
Everything you need before going to production:
- Structured JSON logging
- Request timing and metrics
- Error tracking with full context
- Health check endpoints
- Graceful degradation patterns

---

## Production Checklist

- [ ] All tool inputs are validated
- [ ] No secrets hardcoded (use `.env` or secret manager)
- [ ] Errors return user-friendly messages (not stack traces)
- [ ] Logging is structured (JSON)
- [ ] Health check tool exists
- [ ] File operations are sandboxed
- [ ] SQL queries use parameterized inputs
- [ ] Rate limiting implemented for external APIs
- [ ] Tested with `mcp dev` inspector before deployment
