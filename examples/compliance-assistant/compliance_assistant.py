"""Compliance Assistant MCP example."""

from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("compliance-assistant")

CONTROLS = {
    "SOC2-CC6.1": {"status": "partial", "owner": "security-team"},
    "SOC2-CC7.2": {"status": "pass", "owner": "platform-team"},
}

EVIDENCE = []


@mcp.tool()
def fetch_control_status(control_id: str) -> dict:
    """Fetch current status for a compliance control."""
    control = CONTROLS.get(control_id)
    if not control:
        return {"error": f"Control '{control_id}' not found"}
    return {"control_id": control_id, **control}


@mcp.tool()
def collect_evidence(control_id: str, source: str, summary: str) -> dict:
    """Attach evidence summary to a control."""
    if control_id not in CONTROLS:
        return {"error": f"Control '{control_id}' not found"}
    record = {
        "evidence_id": f"EVD-{len(EVIDENCE) + 1:03d}",
        "control_id": control_id,
        "source": source,
        "summary": summary,
        "collected_at": datetime.utcnow().isoformat() + "Z",
    }
    EVIDENCE.append(record)
    return {"ok": True, "evidence": record}


@mcp.tool()
def generate_audit_report(scope: str) -> dict:
    """Generate a lightweight audit report snapshot."""
    report = {
        "scope": scope,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "control_count": len(CONTROLS),
        "evidence_count": len(EVIDENCE),
        "controls": [{"control_id": k, **v} for k, v in CONTROLS.items()],
    }
    return report


if __name__ == "__main__":
    mcp.run()
