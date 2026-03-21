"""Analytics Dashboard Assistant MCP example."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("analytics-dashboard-assistant")

KPI_DEFS = {
    "mrr": "Monthly recurring revenue from active subscriptions.",
    "churn_rate": "Percent of customers lost in a period.",
    "ltv": "Estimated lifetime value per customer.",
}


@mcp.tool()
def run_metric_query(metric: str, start_date: str, end_date: str) -> dict:
    """Run a mock metric query for a time period."""
    metric_key = metric.lower()
    if metric_key not in KPI_DEFS:
        return {"error": f"Unknown metric '{metric}'"}
    mock_value = {
        "mrr": 128400,
        "churn_rate": 3.4,
        "ltv": 7400,
    }[metric_key]
    return {
        "metric": metric_key,
        "start_date": start_date,
        "end_date": end_date,
        "value": mock_value,
    }


@mcp.tool()
def get_kpi_definition(kpi_name: str) -> dict:
    """Get a KPI definition used by analytics dashboards."""
    key = kpi_name.lower()
    definition = KPI_DEFS.get(key)
    if not definition:
        return {"error": f"KPI '{kpi_name}' not found"}
    return {"kpi": key, "definition": definition}


@mcp.tool()
def create_summary(metrics: list[str], period: str) -> dict:
    """Create a summary scaffold for a dashboard period."""
    normalized = [m.lower() for m in metrics]
    known = [m for m in normalized if m in KPI_DEFS]
    return {
        "period": period,
        "metrics_requested": normalized,
        "metrics_included": known,
        "summary": f"Dashboard summary for {period} covering {', '.join(known) if known else 'no known metrics'}.",
    }


if __name__ == "__main__":
    mcp.run()
