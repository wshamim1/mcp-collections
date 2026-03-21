# Real-World MCP Examples

This folder contains complete, practical MCP example projects you can run and extend.

## Implemented Examples

| Example | Path | Real-world use case | Status |
|---|---|---|---|
| Data Analyst Assistant | `examples/data-analyst/` | Ask natural language business questions over sales data using MCP tools | Implemented |
| Research Assistant | `examples/research-assistant/` | Search web knowledge sources, summarize findings, and save notes | Implemented |
| GitHub Assistant | `examples/github-assistant/` | Explore repositories, issues, pull requests, and files through GitHub APIs | Implemented |

## Additional Real-World Example Ideas

These are practical MCP project ideas you can add next.

| Example idea | What it does | Typical MCP tools |
|---|---|---|
| Customer Support Copilot | Looks up tickets, account status, and policy docs | `get_ticket`, `update_ticket`, `search_knowledge_base` |
| Sales CRM Assistant | Finds leads, updates pipeline, drafts follow-ups | `list_leads`, `update_opportunity_stage`, `create_task` |
| Finance Ops Assistant | Approves invoices with policy checks and audit trail | `list_pending_invoices`, `validate_policy`, `approve_invoice` |
| DevOps Incident Assistant | Pulls logs/alerts and runs controlled diagnostics | `get_alerts`, `query_logs`, `run_diagnostic` |
| HR Self-Service Assistant | Handles PTO, policy Q&A, and onboarding workflows | `get_pto_balance`, `submit_pto_request`, `search_policy` |
| Procurement Assistant | Compares vendors and tracks purchase requests | `list_vendors`, `create_purchase_request`, `check_budget` |
| Compliance Assistant | Collects evidence and maps controls to policies | `fetch_control_status`, `collect_evidence`, `generate_audit_report` |
| Analytics Dashboard Assistant | Builds KPI summaries from data warehouse queries | `run_metric_query`, `get_kpi_definition`, `create_summary` |

## How to Run Current Examples

```bash
# Data analyst
cd examples/data-analyst
python data_analyst.py

# Research assistant
cd examples/research-assistant
python research_assistant.py

# GitHub assistant
cd examples/github-assistant
python github_assistant.py
```

Use MCP inspector for interactive testing:

```bash
mcp dev examples/data-analyst/data_analyst.py
mcp dev examples/research-assistant/research_assistant.py
mcp dev examples/github-assistant/github_assistant.py
```
