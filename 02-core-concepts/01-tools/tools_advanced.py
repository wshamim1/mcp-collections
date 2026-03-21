"""
MCP Tools — Advanced Patterns
================================
Advanced tool patterns including:
- Using MCP Context (logging, progress, sampling)
- Image/binary returns
- Multi-step tools
- Tool composition patterns
- Input validation and sanitization

Run with:
    mcp dev tools_advanced.py
"""

import base64
import io
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP, Context, Image
from pydantic import Field

mcp = FastMCP("advanced-tools-demo")


# ─── Pattern 1: Using Context for Logging ─────────────────────────────────────
# The Context object gives tools access to:
# - ctx.info() / ctx.warning() / ctx.error() — structured logging
# - ctx.report_progress() — progress updates to the client
# - ctx.sample() — request LLM completions (powerful for agentic workflows)

@mcp.tool()
async def process_large_dataset(
    data: list[dict],
    ctx: Context,
) -> dict:
    """
    Process a dataset with progress reporting.

    Args:
        data: List of records to process.

    Returns:
        Processing summary with statistics.
    """
    total = len(data)
    await ctx.info(f"Starting to process {total} records...")

    results = []
    errors = 0

    for i, record in enumerate(data):
        # Report progress every 10 records
        if i % 10 == 0:
            await ctx.report_progress(i, total)

        try:
            # Simulate processing
            processed = {k: str(v).upper() if isinstance(v, str) else v for k, v in record.items()}
            results.append(processed)
        except Exception as e:
            errors += 1
            await ctx.warning(f"Error processing record {i}: {e}")

    await ctx.report_progress(total, total)
    await ctx.info(f"Done! Processed {len(results)} records, {errors} errors.")

    return {
        "total": total,
        "processed": len(results),
        "errors": errors,
        "success_rate": f"{(len(results)/total*100):.1f}%",
    }


# ─── Pattern 2: Returning Images ──────────────────────────────────────────────

@mcp.tool()
def generate_simple_chart(
    title: str,
    values: list[float],
    labels: list[str],
) -> Image:
    """
    Generate a simple bar chart as an image.

    Args:
        title: Chart title.
        values: List of numeric values.
        labels: List of labels corresponding to each value.

    Returns:
        A PNG image of the bar chart.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")  # Non-interactive backend
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(labels, values, color="steelblue", edgecolor="white")
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_ylabel("Value")

        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f"{val:.1f}",
                ha="center",
                fontsize=10,
            )

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100)
        plt.close()
        buf.seek(0)

        return Image(data=buf.read(), format="png")
    except ImportError:
        # Graceful fallback if matplotlib not installed
        raise RuntimeError(
            "matplotlib is required for chart generation. "
            "Install with: pip install matplotlib"
        )


# ─── Pattern 3: Annotated Parameters (rich metadata) ─────────────────────────

@mcp.tool()
def calculate_statistics(
    numbers: Annotated[list[float], Field(description="List of numbers to analyze", min_length=1)],
    include_outliers: Annotated[bool, Field(description="Whether to include outlier detection")] = False,
) -> dict:
    """
    Calculate descriptive statistics for a list of numbers.

    Args:
        numbers: At least one number required.
        include_outliers: Set to true to detect outliers using IQR method.

    Returns:
        Dictionary with mean, median, std_dev, min, max, and optionally outliers.
    """
    import statistics

    sorted_nums = sorted(numbers)
    n = len(numbers)
    mean = statistics.mean(numbers)
    median = statistics.median(numbers)
    std_dev = statistics.stdev(numbers) if n > 1 else 0.0
    q1 = sorted_nums[n // 4]
    q3 = sorted_nums[(3 * n) // 4]

    result = {
        "count": n,
        "mean": round(mean, 4),
        "median": round(median, 4),
        "std_dev": round(std_dev, 4),
        "min": min(numbers),
        "max": max(numbers),
        "range": max(numbers) - min(numbers),
        "q1": q1,
        "q3": q3,
    }

    if include_outliers:
        iqr = q3 - q1
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        outliers = [x for x in numbers if x < lower_fence or x > upper_fence]
        result["outliers"] = outliers
        result["outlier_count"] = len(outliers)

    return result


# ─── Pattern 4: Using Context for AI Sampling ─────────────────────────────────
# ctx.sample() lets the server ask the HOST LLM to generate text.
# This enables powerful agentic server-side logic.

@mcp.tool()
async def summarize_text(
    text: str,
    style: str = "concise",
    ctx: Context = None,
) -> str:
    """
    Summarize a long piece of text using the AI model.

    Args:
        text: The text to summarize.
        style: Summary style — "concise", "detailed", or "bullet_points".

    Returns:
        The summarized text.
    """
    style_instructions = {
        "concise": "in 1-2 sentences",
        "detailed": "in 3-5 sentences covering key points",
        "bullet_points": "as 3-5 bullet points",
    }

    instruction = style_instructions.get(style, "concisely")

    if ctx:
        result = await ctx.sample(
            messages=[{
                "role": "user",
                "content": f"Please summarize the following text {instruction}:\n\n{text}"
            }],
            max_tokens=300,
        )
        return result.content
    else:
        # Fallback: simple truncation
        return text[:200] + "..." if len(text) > 200 else text


# ─── Pattern 5: File Operations Tool ─────────────────────────────────────────

@mcp.tool()
def read_text_file(file_path: str, max_lines: int = 100) -> dict:
    """
    Read a text file and return its contents.

    Args:
        file_path: Absolute or relative path to the file.
        max_lines: Maximum number of lines to return. Defaults to 100.

    Returns:
        Dictionary with file contents, line count, and metadata.
    """
    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        return {"error": f"File not found: {file_path}", "content": None}

    if not path.is_file():
        return {"error": f"Path is not a file: {file_path}", "content": None}

    # Security: only allow reading files with safe extensions
    safe_extensions = {".txt", ".md", ".py", ".json", ".yaml", ".yml", ".toml", ".csv", ".log"}
    if path.suffix.lower() not in safe_extensions:
        return {"error": f"File type '{path.suffix}' not allowed for security reasons.", "content": None}

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        total_lines = len(lines)
        content = "".join(lines[:max_lines])

        return {
            "content": content,
            "total_lines": total_lines,
            "lines_returned": min(max_lines, total_lines),
            "truncated": total_lines > max_lines,
            "file_name": path.name,
            "file_size_bytes": path.stat().st_size,
        }
    except UnicodeDecodeError:
        return {"error": "File is not valid UTF-8 text.", "content": None}
    except PermissionError:
        return {"error": "Permission denied reading this file.", "content": None}


if __name__ == "__main__":
    mcp.run()
