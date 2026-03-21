"""Customer Support Copilot MCP example."""

from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("customer-support-copilot")

TICKETS = {
    "T-1001": {"status": "open", "account": "ACME-01", "subject": "Payment failed at checkout"},
    "T-1002": {"status": "pending", "account": "BETA-22", "subject": "Unable to reset password"},
}

KB = [
    {"id": "KB-10", "title": "Card payment troubleshooting", "tags": ["billing", "checkout"]},
    {"id": "KB-12", "title": "Password reset guide", "tags": ["auth", "login"]},
    {"id": "KB-20", "title": "Account status lifecycle", "tags": ["account", "status"]},
]


@mcp.tool()
def get_ticket(ticket_id: str) -> dict:
    """Get ticket details by ticket id."""
    ticket = TICKETS.get(ticket_id)
    if not ticket:
        return {"error": f"Ticket '{ticket_id}' not found"}
    return {"ticket_id": ticket_id, **ticket}


@mcp.tool()
def update_ticket(ticket_id: str, status: str, note: str = "") -> dict:
    """Update ticket status and append an activity note."""
    ticket = TICKETS.get(ticket_id)
    if not ticket:
        return {"error": f"Ticket '{ticket_id}' not found"}
    ticket["status"] = status
    ticket["last_note"] = note
    ticket["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return {"ok": True, "ticket_id": ticket_id, "status": status}


@mcp.tool()
def search_knowledge_base(query: str, limit: int = 5) -> dict:
    """Search support knowledge base by simple keyword match."""
    q = query.lower().strip()
    matches = [
        item for item in KB
        if q in item["title"].lower() or any(q in tag for tag in item["tags"])
    ]
    return {"query": query, "count": len(matches[:limit]), "results": matches[: max(1, limit)]}


if __name__ == "__main__":
    mcp.run()
