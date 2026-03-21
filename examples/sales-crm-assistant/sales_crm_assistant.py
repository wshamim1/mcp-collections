"""Sales CRM Assistant MCP example."""

from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sales-crm-assistant")

LEADS = [
    {"lead_id": "L-001", "name": "Nova Retail", "stage": "new", "value": 18000},
    {"lead_id": "L-002", "name": "Atlas Health", "stage": "qualified", "value": 42000},
    {"lead_id": "L-003", "name": "Pine Labs", "stage": "proposal", "value": 12000},
]

TASKS = []


@mcp.tool()
def list_leads(stage: str = "", limit: int = 10) -> dict:
    """List leads, optionally filtered by stage."""
    leads = LEADS
    if stage:
        leads = [lead for lead in leads if lead["stage"] == stage]
    return {"count": len(leads[:limit]), "leads": leads[: max(1, limit)]}


@mcp.tool()
def update_opportunity_stage(lead_id: str, new_stage: str) -> dict:
    """Update the pipeline stage for a lead."""
    for lead in LEADS:
        if lead["lead_id"] == lead_id:
            lead["stage"] = new_stage
            lead["updated_at"] = datetime.utcnow().isoformat() + "Z"
            return {"ok": True, "lead_id": lead_id, "stage": new_stage}
    return {"error": f"Lead '{lead_id}' not found"}


@mcp.tool()
def create_task(lead_id: str, title: str, due_date: str = "") -> dict:
    """Create a CRM follow-up task."""
    task = {
        "task_id": f"TASK-{len(TASKS) + 1:03d}",
        "lead_id": lead_id,
        "title": title,
        "due_date": due_date,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    TASKS.append(task)
    return {"ok": True, "task": task}


if __name__ == "__main__":
    mcp.run()
