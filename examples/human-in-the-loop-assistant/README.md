# Human-in-the-Loop Assistant

A practical MCP example showing how to gate sensitive actions behind explicit human approval.

## What It Demonstrates

This example separates **proposal**, **approval**, and **execution**:

1. The model proposes an action.
2. A human reviews and either approves or rejects it.
3. Only approved actions can be executed.

This is a good pattern for:
- finance approvals
- procurement requests
- production changes
- external communications
- HR or admin operations

## Tools

- `propose_action`
- `list_pending_actions`
- `approve_action`
- `reject_action`
- `execute_approved_action`
- `list_completed_actions`

## Run

### Option 1: Inspector
```bash
cd examples/human-in-the-loop-assistant
mcp dev human_in_the_loop_assistant.py
```

### Option 2: Start as Server
```bash
cd examples/human-in-the-loop-assistant
python human_in_the_loop_assistant.py
```

## Example Workflow

1. Propose an action:
```json
{
  "action_type": "send_refund",
  "target": "order-10025",
  "summary": "Refund customer due to duplicate charge"
}
```

2. Approve it:
```json
{
  "action_id": "ACT-001",
  "approver": "finance-manager",
  "approval_note": "Valid refund, proceed"
}
```

3. Execute it:
```json
{
  "action_id": "ACT-001"
}
```

If you try to execute before approval, the server returns a blocking error instead of performing the action.
