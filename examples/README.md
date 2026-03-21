# Real-World MCP Examples

This folder contains complete, practical MCP example projects you can run and extend.

## Implemented Examples

| Example | Path | Real-world use case | Status |
|---|---|---|---|
| Data Analyst Assistant | `examples/data-analyst/` | Ask natural language business questions over sales data using MCP tools | Implemented |
| Research Assistant | `examples/research-assistant/` | Search web knowledge sources, summarize findings, and save notes | Implemented |
| GitHub Assistant | `examples/github-assistant/` | Explore repositories, issues, pull requests, and files through GitHub APIs | Implemented |
| Customer Support Copilot | `examples/customer-support-copilot/` | Looks up tickets, account status, and policy docs | Starter template |
| Sales CRM Assistant | `examples/sales-crm-assistant/` | Finds leads, updates pipeline, drafts follow-ups | Starter template |
| Finance Ops Assistant | `examples/finance-ops-assistant/` | Approves invoices with policy checks and audit trail | Starter template |
| DevOps Incident Assistant | `examples/devops-incident-assistant/` | Pulls logs/alerts and runs controlled diagnostics | Starter template |
| HR Self-Service Assistant | `examples/hr-self-service-assistant/` | Handles PTO, policy Q&A, and onboarding workflows | Starter template |
| Procurement Assistant | `examples/procurement-assistant/` | Compares vendors and tracks purchase requests | Starter template |
| Compliance Assistant | `examples/compliance-assistant/` | Collects evidence and maps controls to policies | Starter template |
| Analytics Dashboard Assistant | `examples/analytics-dashboard-assistant/` | Builds KPI summaries from data warehouse queries | Starter template |
| Human-in-the-Loop Assistant | `examples/human-in-the-loop-assistant/` | Proposes actions that require explicit human approval before execution | Starter template |

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

# Customer support copilot
cd examples/customer-support-copilot
python customer_support_copilot.py

# Sales CRM assistant
cd examples/sales-crm-assistant
python sales_crm_assistant.py

# Finance ops assistant
cd examples/finance-ops-assistant
python finance_ops_assistant.py

# DevOps incident assistant
cd examples/devops-incident-assistant
python devops_incident_assistant.py

# HR self-service assistant
cd examples/hr-self-service-assistant
python hr_self_service_assistant.py

# Procurement assistant
cd examples/procurement-assistant
python procurement_assistant.py

# Compliance assistant
cd examples/compliance-assistant
python compliance_assistant.py

# Analytics dashboard assistant
cd examples/analytics-dashboard-assistant
python analytics_dashboard_assistant.py

# Human-in-the-loop assistant
cd examples/human-in-the-loop-assistant
python human_in_the_loop_assistant.py
```

Use MCP inspector for interactive testing:

```bash
mcp dev examples/data-analyst/data_analyst.py
mcp dev examples/research-assistant/research_assistant.py
mcp dev examples/github-assistant/github_assistant.py
mcp dev examples/customer-support-copilot/customer_support_copilot.py
mcp dev examples/sales-crm-assistant/sales_crm_assistant.py
mcp dev examples/finance-ops-assistant/finance_ops_assistant.py
mcp dev examples/devops-incident-assistant/devops_incident_assistant.py
mcp dev examples/hr-self-service-assistant/hr_self_service_assistant.py
mcp dev examples/procurement-assistant/procurement_assistant.py
mcp dev examples/compliance-assistant/compliance_assistant.py
mcp dev examples/analytics-dashboard-assistant/analytics_dashboard_assistant.py
mcp dev examples/human-in-the-loop-assistant/human_in_the_loop_assistant.py
```
