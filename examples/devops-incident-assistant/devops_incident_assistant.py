"""DevOps Incident Assistant MCP example."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("devops-incident-assistant")

ALERTS = [
    {"id": "A-001", "service": "api", "severity": "high", "summary": "HTTP 500 spike"},
    {"id": "A-002", "service": "worker", "severity": "medium", "summary": "Queue lag increasing"},
    {"id": "A-003", "service": "db", "severity": "high", "summary": "Replication delay"},
]

LOGS = [
    {"service": "api", "line": "error timeout upstream payments"},
    {"service": "worker", "line": "warn retrying job 8b12"},
    {"service": "db", "line": "error replication slot lag threshold"},
]


@mcp.tool()
def get_alerts(service: str = "", severity: str = "") -> dict:
    """List active alerts, optionally filtering by service or severity."""
    items = ALERTS
    if service:
        items = [a for a in items if a["service"] == service]
    if severity:
        items = [a for a in items if a["severity"] == severity]
    return {"count": len(items), "alerts": items}


@mcp.tool()
def query_logs(service: str, contains: str = "", limit: int = 20) -> dict:
    """Query recent logs for a service with optional text filter."""
    items = [l for l in LOGS if l["service"] == service]
    if contains:
        c = contains.lower()
        items = [l for l in items if c in l["line"].lower()]
    return {"service": service, "count": len(items[:limit]), "logs": items[: max(1, limit)]}


@mcp.tool()
def run_diagnostic(service: str) -> dict:
    """Run a lightweight diagnostic checklist for a service."""
    checks = [
        {"check": "health_endpoint", "status": "pass"},
        {"check": "latency_budget", "status": "warn" if service == "api" else "pass"},
        {"check": "error_rate", "status": "fail" if service == "db" else "pass"},
    ]
    return {"service": service, "checks": checks}


if __name__ == "__main__":
    mcp.run()
