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

## 6. When should I use tools vs resources vs prompts?

Use:

- `tools` for actions or computations, such as querying a service, creating a record, or triggering a workflow
- `resources` for readable data, such as files, database views, configuration, or reference documents
- `prompts` for reusable templates that guide how a model should perform a repeated task

If the model needs to do something, use a tool. If it needs to read something, use a resource. If it needs reusable instruction scaffolding, use a prompt.

## 7. Should I build one large MCP server or several smaller ones?

Usually, several smaller domain-based servers are easier to operate.

Examples:

- one server for customer data
- one server for billing
- one server for document search

Smaller servers improve ownership, security boundaries, testing, and deployment independence. A single large server can be fine early on, but often becomes harder to maintain as the number of tools grows.

## 8. Can multiple AI models use the same MCP server?

Yes. That is one of the main advantages of MCP.

Your MCP server can expose the same tools to different model clients, such as Claude, OpenAI-based apps, or local models through Ollama, as long as the client side supports MCP.

This reduces duplication and prevents building separate integrations for each model provider.

## 9. How should I handle authentication for external consumers?

Common approaches include:

- API keys for simple service-to-service access
- OAuth for user-delegated access
- JWT or internal identity tokens for enterprise environments
- SSO-backed gateway or reverse proxy for internal teams

For public or partner-facing deployments, avoid anonymous access. Combine authentication with tool-level authorization so users can only call the capabilities they are allowed to use.

## 10. Can I expose write operations safely?

Yes, but write operations need stronger controls than read-only tools.

Recommended safeguards:

- explicit allowlists for writable operations
- approval steps for sensitive actions
- idempotency for repeatable requests
- audit logging for every mutation
- role checks before execution
- narrow scopes such as updating only specific records or fields

Avoid generic write tools like `execute_any_sql` unless they are heavily sandboxed and restricted.

## 11. How do I test an MCP server before production?

Use multiple layers of testing:

- `mcp dev` for interactive inspection and manual validation
- unit tests for business logic behind each tool
- integration tests for server behavior and downstream systems
- permission tests to verify role boundaries
- failure-path tests for timeouts, invalid inputs, and dependency errors

Testing only happy paths is not enough. The dangerous failures usually happen in auth, retries, malformed input, and partial downstream outages.

## 12. What should I log for MCP requests?

At minimum, log:

- request ID
- caller identity
- tool name
- input validation result
- latency
- success or failure status
- downstream dependency errors

For sensitive systems, also keep audit logs showing who invoked what, when, and with what outcome.

## 13. How do I prevent prompt injection or unsafe tool usage?

MCP helps by defining explicit tool boundaries, but it does not solve prompt injection by itself.

You still need:

- strict authorization on the server side
- validation of all tool arguments
- policy checks before dangerous actions
- output filtering where necessary
- separation between trusted instructions and untrusted user content

Never assume that because a model asked for a tool call, the call should be allowed.

## 14. Can MCP run only inside my company network?

Yes. Many enterprise MCP deployments should be internal only.

Common patterns:

- run the server on a private VPC or internal subnet
- expose it only through VPN or zero-trust access
- put it behind an internal API gateway
- restrict access by identity, IP range, or service account

MCP does not require public internet exposure.

## 15. What is the difference between MCP and a normal REST API?

A REST API is a general application interface. MCP is a standard interface specifically designed for model-to-tool interaction.

Key differences:

- MCP has built-in concepts like tools, resources, prompts, and capability discovery
- MCP is designed for AI clients deciding dynamically what to call
- MCP standardizes how clients list and use capabilities across providers
- REST APIs often still sit behind MCP servers as the underlying implementation

In practice, many teams wrap existing REST or database operations with MCP so models can use them in a structured way.

## 16. What are different MCP deployment options?

Common deployment options, from simplest to most production-ready:

### Option A: Local `stdio` process

- Client launches MCP server as a local child process
- Communication happens via stdin/stdout
- Best for local development and personal workflows

Pros:

- simplest setup
- no network exposure
- fast iteration

Cons:

- not easily shared across a team
- tied to local machine/runtime

### Option B: Remote server over SSE/HTTP

- MCP server runs as a network service
- Clients connect remotely over HTTP/SSE
- Best for team-shared services

Pros:

- centralized operations and governance
- one service can support multiple clients

Cons:

- requires stronger security and ops controls

### Option C: Private internal deployment (VPC/VPN)

- Remote server but reachable only inside private network
- Protected by VPN, private subnet, or zero-trust access

Pros:

- strong security boundary
- good fit for sensitive internal systems

Cons:

- requires internal networking/platform setup

### Option D: API gateway in front of MCP server

- Gateway handles auth, TLS, rate limits, and policy
- MCP server focuses on tool logic

Pros:

- centralized access control
- standardized security and observability

Cons:

- more platform complexity

### Option E: Containerized deployment (Docker/Kubernetes)

- MCP server packaged as container image
- Deployed to ECS/AKS/GKE/Kubernetes or similar

Pros:

- repeatable deployment
- scaling and resilience support

Cons:

- needs container platform maturity

### Option F: Serverless-backed MCP tools

- MCP layer routes tool calls to serverless functions
- Useful for bursty, event-driven workloads

Pros:

- cost-efficient at low/variable traffic

Cons:

- cold starts
- more complexity for stateful flows

### Recommended adoption path

1. Start local with `stdio` and `mcp dev`
2. Move to internal remote service (SSE) for shared usage
3. Add gateway + auth + logging + rate limits
4. Containerize and scale based on traffic and reliability needs
