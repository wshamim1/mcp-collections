"""
Production MCP Server — Logging, Error Handling & Monitoring
=============================================================
Best practices for production-grade MCP servers:
- Structured logging (JSON format)
- Request/response timing
- Error tracking with context
- Health monitoring
- Graceful degradation

Run:
    LOG_LEVEL=DEBUG python production_server.py
"""

import json
import logging
import os
import time
import traceback
from contextlib import asynccontextmanager
from datetime import datetime
from functools import wraps
from typing import Any, Callable

from mcp.server.fastmcp import FastMCP, Context

# ─── Structured Logger ──────────────────────────────────────────────────────

class JSONFormatter(logging.Formatter):
    """Formats log records as JSON for log aggregation (Datadog, CloudWatch, etc.)."""

    def format(self, record: logging.LogRecord) -> str:
        log_dict = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            log_dict["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra"):
            log_dict.update(record.extra)
        return json.dumps(log_dict)


def setup_logging():
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logging.basicConfig(level=log_level, handlers=[handler])
    return logging.getLogger("mcp-production")


logger = setup_logging()

# ─── Metrics (in-memory, replace with Prometheus/Datadog in prod) ────────────

_metrics = {
    "requests_total": 0,
    "requests_failed": 0,
    "tool_calls": {},       # tool_name → count
    "tool_errors": {},      # tool_name → count
    "response_times_ms": [],
}


def _record_call(tool_name: str, duration_ms: float, success: bool):
    _metrics["requests_total"] += 1
    _metrics["response_times_ms"].append(duration_ms)
    # Keep only last 1000 for sliding window
    if len(_metrics["response_times_ms"]) > 1000:
        _metrics["response_times_ms"].pop(0)

    _metrics["tool_calls"][tool_name] = _metrics["tool_calls"].get(tool_name, 0) + 1
    if not success:
        _metrics["requests_failed"] += 1
        _metrics["tool_errors"][tool_name] = _metrics["tool_errors"].get(tool_name, 0) + 1


# ─── Observability Decorator ─────────────────────────────────────────────────

def monitored(func: Callable) -> Callable:
    """
    Decorator adding logging, timing, and error tracking to any tool.
    Wrap your tools with this in production.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        tool_name = func.__name__
        start = time.monotonic()
        logger.info(f"Tool called: {tool_name}", extra={"tool": tool_name, "args": str(kwargs)[:200]})

        try:
            result = await func(*args, **kwargs) if asyncio_is_async(func) else func(*args, **kwargs)
            duration_ms = round((time.monotonic() - start) * 1000, 2)
            _record_call(tool_name, duration_ms, success=True)
            logger.info(
                f"Tool completed: {tool_name}",
                extra={"tool": tool_name, "duration_ms": duration_ms}
            )
            return result
        except Exception as e:
            duration_ms = round((time.monotonic() - start) * 1000, 2)
            _record_call(tool_name, duration_ms, success=False)
            logger.error(
                f"Tool failed: {tool_name} — {e}",
                extra={
                    "tool": tool_name,
                    "duration_ms": duration_ms,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                }
            )
            return {"error": f"Tool '{tool_name}' encountered an error: {str(e)}"}

    return wrapper


def asyncio_is_async(func) -> bool:
    import asyncio
    return asyncio.iscoroutinefunction(func)


# ─── Server ───────────────────────────────────────────────────────────────────

mcp = FastMCP("production-server")


@mcp.tool()
@monitored
async def process_data(data: list[dict], operation: str) -> dict:
    """
    Process a list of records with observability.

    Args:
        data: List of data records.
        operation: Operation to perform — "count", "sum_values", "filter_non_empty".
    """
    import asyncio

    if operation == "count":
        return {"result": len(data), "operation": operation}

    elif operation == "sum_values":
        total = sum(
            v for record in data for v in record.values() if isinstance(v, (int, float))
        )
        return {"result": total, "operation": operation}

    elif operation == "filter_non_empty":
        filtered = [r for r in data if any(v for v in r.values())]
        return {"result": filtered, "count": len(filtered), "operation": operation}

    else:
        return {"error": f"Unknown operation: {operation}. Use: count, sum_values, filter_non_empty"}


@mcp.tool()
def get_health() -> dict:
    """
    Health check endpoint — returns server status and basic metrics.
    Use this to confirm the server is running correctly.
    """
    times = _metrics["response_times_ms"]
    avg_ms = round(sum(times) / len(times), 2) if times else 0
    p99_ms = sorted(times)[int(len(times) * 0.99)] if len(times) > 100 else (max(times) if times else 0)

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {
            "requests_total": _metrics["requests_total"],
            "requests_failed": _metrics["requests_failed"],
            "success_rate": (
                f"{(1 - _metrics['requests_failed'] / max(_metrics['requests_total'], 1)) * 100:.1f}%"
            ),
            "avg_response_ms": avg_ms,
            "p99_response_ms": p99_ms,
            "top_tools": sorted(
                _metrics["tool_calls"].items(),
                key=lambda x: x[1],
                reverse=True,
            )[:5],
        },
    }


@mcp.tool()
def get_metrics() -> dict:
    """Detailed metrics for all tools."""
    return {
        "tool_invocations": _metrics["tool_calls"],
        "tool_errors": _metrics["tool_errors"],
        "total_requests": _metrics["requests_total"],
        "total_errors": _metrics["requests_failed"],
    }


if __name__ == "__main__":
    logger.info("Production MCP server starting", extra={"version": "1.0.0"})
    mcp.run()
