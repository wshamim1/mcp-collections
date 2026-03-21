# MCP Architecture

## Overview

Understanding MCP's architecture is key to building robust, scalable AI integrations. This section covers:

1. **Client-Server Model** — How components communicate
2. **Transport Layers** — stdio, SSE, WebSocket
3. **Protocol Messages** — The JSON-RPC 2.0 layer
4. **Lifecycle Management** — Connection and session lifecycle
5. **Security Model** — Trust boundaries and sandboxing

---

## High-Level Architecture

```mermaid
graph TB
    subgraph Host["MCP HOST"]
        App["AI Application<br/>• Claude Desktop<br/>• VS Code<br/>• Custom App"]
        Client["MCP Client<br/>• Manages connections<br/>• Routes tool calls<br/>• Protocol handler<br/>• Capability negotiation"]
        App <-->|Request/Response| Client
    end
    
    Client -->|Transport| Transport["Transport Layer<br/>stdio | SSE | WebSocket"]
    
    Transport --> ServerA["MCP Server A<br/>🔧 Tools: search_web, fetch_url<br/>📂 Resources: web://{url}"]
    Transport --> ServerB["MCP Server B<br/>🔧 Tools: query_db, write_record<br/>📂 Resources: db://{table}"]
    Transport --> ServerC["MCP Server C<br/>🔧 Tools: send_email, read_email"]
    
    ServerA --> ExtA["External APIs"]
    ServerB --> ExtB["SQL Database"]
    ServerC --> ExtC["Email Service"]
    
    style Host fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style Client fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    style ServerA fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style ServerB fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style ServerC fill:#fff3e0,stroke:#f57c00,stroke-width:2px
```

---

## Transport Layers

### 1. stdio (Standard I/O) — Most Common

Used for **local** MCP servers launched as child processes.

```mermaid
sequenceDiagram
    participant Host as Host Process
    participant Server as Server Process
    
    Host->>Server: spawn(python server.py)
    
    Host->>Server: stdin: JSON-RPC message
    Server->>Host: stdout: JSON-RPC response
    
    Host->>Server: stdin: next message
    Server->>Host: stdout: response
```

**When to use:**
- Local tools (filesystem, databases)
- Claude Desktop / VS Code integrations
- Development and testing
- Security-sensitive operations

```python
# Client connecting via stdio
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters

params = StdioServerParameters(
    command="python",
    args=["server.py"],
    env={"MY_VAR": "value"},
)
async with stdio_client(params) as (read, write):
    ...
```

### 2. SSE (Server-Sent Events) — Remote Servers

Used for **remote** MCP servers accessible over HTTP.

```mermaid
sequenceDiagram
    participant Host as Host (Client)
    participant Server as Remote Server
    
    Host->>Server: GET /sse (long-lived)
    loop SSE Stream
        Server->>Host: SSE stream events
    end
    
    Host->>Server: POST /message (send command)
    Server->>Host: SSE event: response
```

**When to use:**
- Shared servers in a team
- SaaS tool integrations
- Servers with startup costs (ML models, DB connections)
- Remote services accessed over network

```python
# Client connecting via SSE
from mcp.client.sse import sse_client

async with sse_client("http://localhost:8000/sse") as (read, write):
    ...
```

### 3. WebSocket — Bidirectional Streaming

Full-duplex communication for high-frequency, real-time scenarios.

---

## Protocol: JSON-RPC 2.0

All MCP messages follow the JSON-RPC 2.0 standard:

### Request (Client → Server)
```json
{
  "jsonrpc": "2.0",
  "id": "req-1",
  "method": "tools/call",
  "params": {
    "name": "get_weather",
    "arguments": {
      "city": "Tokyo"
    }
  }
}
```

### Response (Server → Client)
```json
{
  "jsonrpc": "2.0",
  "id": "req-1",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"temperature\": \"22°C\", \"condition\": \"Sunny\"}"
      }
    ]
  }
}
```

### Notification (no response expected)
```json
{
  "jsonrpc": "2.0",
  "method": "notifications/tools/list_changed"
}
```

---

## Connection Lifecycle

```mermaid
sequenceDiagram
    participant Client
    participant Server
    
    Client->>Server: initialize
    Note over Client,Server: "Hello, here are my capabilities"
    Server->>Client: initialized
    Note over Server,Client: "Hello, here are MY capabilities"
    
    Client->>Server: tools/list
    Note over Client,Server: "What tools do you have?"
    Server->>Client: tools/list result
    Note over Server,Client: "Here are my tools..."
    
    Client->>Server: tools/call
    Note over Client,Server: "Call this tool with these args"
    Server->>Client: tools/call result
    Note over Server,Client: "Here is the result"
    
    loop Many Exchanges
        Client->>Server: Additional tool calls
        Server->>Client: Responses
    end
    
    Client->>Server: (connection close)
    Note over Client,Server: Session ends
```

---

## Capability Negotiation

During initialization, client and server exchange capabilities:

```python
# Server declares capabilities
server_capabilities = {
    "tools": {"listChanged": True},       # Tools can change dynamically
    "resources": {"subscribe": True},      # Clients can subscribe to changes
    "prompts": {"listChanged": False},     # Prompts are static
    "logging": {},                         # Supports log messages
    "sampling": {},                        # Can request LLM sampling
}
```

---

## Security Architecture

```mermaid
graph TB
    subgraph Host["HOST (trusted zone)"]
        Model["AI Model<br/>(reasoning)"]
        Client["MCP Client<br/>(protocol)"]
        Consent["User consent layer"]
        Model --- Client --- Consent
    end
    
    Consent -->|Only approved calls| Server
    
    subgraph Server["SERVER (sandboxed)"]
        Process["Tools in isolated process"]
        Decl["Declared capabilities only"]
        Approve["User approves tool calls"]
        Access["Cannot access host directly"]
    end
    
    Server -->|Constrained access| External["External World"]
    
    style Host fill:#c8e6c9,stroke:#388e3c,stroke-width:3px
    style Server fill:#ffccbc,stroke:#d84315,stroke-width:3px
    style External fill:#fff3e0,stroke:#f57c00
```

**Key Security Principles:**
1. **Least Privilege** — Servers only get what they need
2. **User Consent** — Sensitive operations require user approval
3. **Process Isolation** — Servers run as separate processes
4. **No Direct LLM Access** — Servers can't control the AI directly
5. **Input Validation** — Always validate inputs at server boundary

---

## Files in This Section

- `client_server_demo.py` — Shows full client-server interaction
- `sse_server.py` — Remote server using SSE transport
- `security_patterns.py` — Secure tool implementation patterns

---

## Next Steps

- [Filesystem Server →](../04-intermediate/01-filesystem-server/README.md)
- [Database Server →](../04-intermediate/02-database-server/README.md)
