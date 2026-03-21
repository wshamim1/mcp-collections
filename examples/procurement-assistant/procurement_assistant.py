"""Procurement Assistant MCP example."""

from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("procurement-assistant")

VENDORS = [
    {"vendor_id": "V-01", "name": "Acme Supplies", "category": "hardware"},
    {"vendor_id": "V-02", "name": "CloudMart", "category": "software"},
    {"vendor_id": "V-03", "name": "OfficePro", "category": "office"},
]

BUDGETS = {
    "engineering": 50000,
    "finance": 20000,
    "operations": 35000,
}

REQUESTS = []


@mcp.tool()
def list_vendors(category: str = "", limit: int = 10) -> dict:
    """List procurement vendors, optionally by category."""
    items = VENDORS
    if category:
        items = [v for v in items if v["category"] == category]
    return {"count": len(items[:limit]), "vendors": items[: max(1, limit)]}


@mcp.tool()
def create_purchase_request(requester: str, item: str, amount: float, vendor_id: str = "") -> dict:
    """Create a purchase request entry."""
    req = {
        "request_id": f"PR-{len(REQUESTS) + 1:03d}",
        "requester": requester,
        "item": item,
        "amount": amount,
        "vendor_id": vendor_id,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    REQUESTS.append(req)
    return {"ok": True, "request": req}


@mcp.tool()
def check_budget(department: str, amount: float) -> dict:
    """Check if requested amount fits within department budget."""
    budget = BUDGETS.get(department)
    if budget is None:
        return {"error": f"Department '{department}' not found"}
    return {
        "department": department,
        "requested": amount,
        "available_budget": budget,
        "within_budget": amount <= budget,
    }


if __name__ == "__main__":
    mcp.run()
