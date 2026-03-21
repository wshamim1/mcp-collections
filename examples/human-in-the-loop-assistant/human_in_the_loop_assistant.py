"""Human-in-the-Loop Assistant MCP example.

Demonstrates a gated workflow where the model can propose actions,
but execution only happens after explicit human approval.
"""

from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("human-in-the-loop-assistant")

PENDING_ACTIONS: dict[str, dict] = {}
COMPLETED_ACTIONS: list[dict] = []
NEXT_ID = 1


def _new_action_id() -> str:
    global NEXT_ID
    action_id = f"ACT-{NEXT_ID:03d}"
    NEXT_ID += 1
    return action_id


@mcp.tool()
def propose_action(action_type: str, target: str, summary: str, requested_by: str = "ai-agent") -> dict:
    """Create a pending action that requires human review before execution."""
    action_id = _new_action_id()
    action = {
        "action_id": action_id,
        "action_type": action_type,
        "target": target,
        "summary": summary,
        "requested_by": requested_by,
        "status": "pending_approval",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    PENDING_ACTIONS[action_id] = action
    return {
        "ok": True,
        "message": "Action proposed and waiting for human approval.",
        "action": action,
    }


@mcp.tool()
def list_pending_actions(limit: int = 20) -> dict:
    """List all actions waiting for human approval."""
    actions = list(PENDING_ACTIONS.values())[: max(1, limit)]
    return {"count": len(actions), "pending_actions": actions}


@mcp.tool()
def approve_action(action_id: str, approver: str, approval_note: str = "") -> dict:
    """Approve a pending action so it can be executed."""
    action = PENDING_ACTIONS.get(action_id)
    if not action:
        return {"error": f"Action '{action_id}' not found"}

    action["status"] = "approved"
    action["approved_by"] = approver
    action["approval_note"] = approval_note
    action["approved_at"] = datetime.utcnow().isoformat() + "Z"
    return {"ok": True, "action": action}


@mcp.tool()
def reject_action(action_id: str, approver: str, reason: str) -> dict:
    """Reject a pending action and record the reason."""
    action = PENDING_ACTIONS.get(action_id)
    if not action:
        return {"error": f"Action '{action_id}' not found"}

    action["status"] = "rejected"
    action["rejected_by"] = approver
    action["rejection_reason"] = reason
    action["rejected_at"] = datetime.utcnow().isoformat() + "Z"
    COMPLETED_ACTIONS.append(action.copy())
    del PENDING_ACTIONS[action_id]
    return {"ok": True, "action": action}


@mcp.tool()
def execute_approved_action(action_id: str) -> dict:
    """Execute an action only if it has already been approved by a human."""
    action = PENDING_ACTIONS.get(action_id)
    if not action:
        return {"error": f"Action '{action_id}' not found"}

    if action["status"] != "approved":
        return {
            "error": "Action cannot be executed until a human approves it.",
            "action_id": action_id,
            "status": action["status"],
        }

    action["status"] = "executed"
    action["executed_at"] = datetime.utcnow().isoformat() + "Z"
    action["execution_result"] = f"Executed {action['action_type']} on {action['target']}"
    COMPLETED_ACTIONS.append(action.copy())
    del PENDING_ACTIONS[action_id]
    return {"ok": True, "action": action}


@mcp.tool()
def list_completed_actions(limit: int = 20) -> dict:
    """List actions that have been rejected or executed."""
    actions = COMPLETED_ACTIONS[: max(1, limit)]
    return {"count": len(actions), "completed_actions": actions}


if __name__ == "__main__":
    mcp.run()
