"""Finance Ops Assistant MCP example."""

from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("finance-ops-assistant")

INVOICES = {
    "INV-100": {"vendor": "CloudHost", "amount": 4200, "status": "pending"},
    "INV-101": {"vendor": "DataTools", "amount": 8900, "status": "pending"},
    "INV-102": {"vendor": "DesignPro", "amount": 650, "status": "pending"},
}


@mcp.tool()
def list_pending_invoices(limit: int = 10) -> dict:
    """List pending invoices awaiting review."""
    items = [
        {"invoice_id": invoice_id, **inv}
        for invoice_id, inv in INVOICES.items()
        if inv["status"] == "pending"
    ]
    return {"count": len(items[:limit]), "invoices": items[: max(1, limit)]}


@mcp.tool()
def validate_policy(invoice_id: str) -> dict:
    """Validate invoice against simple finance policy rules."""
    invoice = INVOICES.get(invoice_id)
    if not invoice:
        return {"error": f"Invoice '{invoice_id}' not found"}

    requires_manager = invoice["amount"] > 5000
    return {
        "invoice_id": invoice_id,
        "policy_pass": not requires_manager,
        "requires_manager_approval": requires_manager,
        "reason": "Manager approval required above 5000" if requires_manager else "Policy checks passed",
    }


@mcp.tool()
def approve_invoice(invoice_id: str, approver: str) -> dict:
    """Approve an invoice and record approval metadata."""
    invoice = INVOICES.get(invoice_id)
    if not invoice:
        return {"error": f"Invoice '{invoice_id}' not found"}

    invoice["status"] = "approved"
    invoice["approved_by"] = approver
    invoice["approved_at"] = datetime.utcnow().isoformat() + "Z"
    return {"ok": True, "invoice_id": invoice_id, "status": "approved"}


if __name__ == "__main__":
    mcp.run()
