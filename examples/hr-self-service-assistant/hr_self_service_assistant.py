"""HR Self-Service Assistant MCP example."""

from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hr-self-service-assistant")

PTO = {
    "E-100": {"name": "Alice", "balance_days": 12},
    "E-101": {"name": "Bob", "balance_days": 6},
}

POLICIES = [
    {"id": "P-01", "title": "Paid Time Off Policy"},
    {"id": "P-02", "title": "Remote Work Guidelines"},
    {"id": "P-03", "title": "New Hire Onboarding Checklist"},
]

REQUESTS = []


@mcp.tool()
def get_pto_balance(employee_id: str) -> dict:
    """Get current PTO balance for an employee."""
    employee = PTO.get(employee_id)
    if not employee:
        return {"error": f"Employee '{employee_id}' not found"}
    return {"employee_id": employee_id, **employee}


@mcp.tool()
def submit_pto_request(employee_id: str, start_date: str, end_date: str, reason: str = "") -> dict:
    """Submit a PTO request record."""
    if employee_id not in PTO:
        return {"error": f"Employee '{employee_id}' not found"}
    request = {
        "request_id": f"PTO-{len(REQUESTS) + 1:03d}",
        "employee_id": employee_id,
        "start_date": start_date,
        "end_date": end_date,
        "reason": reason,
        "status": "submitted",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    REQUESTS.append(request)
    return {"ok": True, "request": request}


@mcp.tool()
def search_policy(query: str, limit: int = 5) -> dict:
    """Search policy titles by keyword."""
    q = query.lower().strip()
    matches = [p for p in POLICIES if q in p["title"].lower()]
    return {"query": query, "count": len(matches[:limit]), "policies": matches[: max(1, limit)]}


if __name__ == "__main__":
    mcp.run()
