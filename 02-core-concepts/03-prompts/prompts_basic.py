"""
MCP Prompts — Basic Patterns
==============================
Demonstrates prompt patterns:
- Simple parameterized prompts
- Multi-turn conversation prompts
- System + user message prompts
- Prompts for common dev workflows

Run with:
    mcp dev prompts_basic.py
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("prompts-demo")


# ─── Pattern 1: Simple User Message Prompt ────────────────────────────────────

@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """
    Generate a code review for the given code snippet.

    Args:
        language: Programming language (e.g., python, javascript).
        code: The code to review.
    """
    return (
        f"Please review this {language} code and provide detailed feedback:\n\n"
        f"```{language}\n{code}\n```\n\n"
        "Cover these aspects:\n"
        "1. **Correctness** — Does the code do what it intends?\n"
        "2. **Style** — Does it follow {language} conventions?\n"
        "3. **Performance** — Any obvious inefficiencies?\n"
        "4. **Security** — Any vulnerabilities or risks?\n"
        "5. **Improvements** — Specific refactoring suggestions with examples."
    )


# ─── Pattern 2: Translation Prompt ────────────────────────────────────────────

@mcp.prompt()
def translate_text(text: str, target_language: str, formality: str = "neutral") -> str:
    """
    Translate text to another language with a specified formality level.

    Args:
        text: The text to translate.
        target_language: The target language (e.g., Spanish, French, Japanese).
        formality: Formality level — "formal", "neutral", or "casual".
    """
    formality_instruction = {
        "formal": "Use formal, professional language.",
        "neutral": "Use natural, everyday language.",
        "casual": "Use casual, conversational language.",
    }.get(formality, "Use natural language.")

    return (
        f"Translate the following text to {target_language}.\n"
        f"{formality_instruction}\n\n"
        f"Text to translate:\n{text}\n\n"
        "Provide only the translation, no explanations."
    )


# ─── Pattern 3: Data Analysis Prompt ──────────────────────────────────────────

@mcp.prompt()
def analyze_data(data_description: str, analysis_goal: str) -> str:
    """
    Generate a data analysis plan and insights.

    Args:
        data_description: Description of the dataset (columns, size, source).
        analysis_goal: What you want to learn from the data.
    """
    return (
        f"You are a data analyst. I have a dataset with this description:\n\n"
        f"{data_description}\n\n"
        f"My analysis goal is: {analysis_goal}\n\n"
        "Please:\n"
        "1. Suggest the most relevant analyses to run\n"
        "2. Identify potential data quality issues to check\n"
        "3. Recommend visualizations that would be most informative\n"
        "4. Provide Python code using pandas/matplotlib to perform the analysis\n"
        "5. Describe what insights to look for in the results"
    )


# ─── Pattern 4: Debug Helper Prompt ───────────────────────────────────────────

@mcp.prompt()
def debug_error(
    error_message: str,
    code_context: str,
    language: str = "python",
) -> str:
    """
    Help debug an error with code context.

    Args:
        error_message: The full error message or stack trace.
        code_context: The relevant code where the error occurred.
        language: Programming language.
    """
    return (
        f"I'm getting this error in my {language} code:\n\n"
        f"**Error:**\n```\n{error_message}\n```\n\n"
        f"**Code Context:**\n```{language}\n{code_context}\n```\n\n"
        "Please:\n"
        "1. Explain what is causing this error\n"
        "2. Show the corrected code\n"
        "3. Explain why the fix works\n"
        "4. Mention any related pitfalls to avoid"
    )


# ─── Pattern 5: Document Generation Prompt ────────────────────────────────────

@mcp.prompt()
def generate_readme(
    project_name: str,
    project_description: str,
    tech_stack: str,
    features: str,
) -> str:
    """
    Generate a professional README.md for a project.

    Args:
        project_name: Name of the project.
        project_description: Short description of what it does.
        tech_stack: Technologies used (comma-separated).
        features: Key features (comma-separated or bullet list).
    """
    return (
        f"Generate a professional GitHub README.md for this project:\n\n"
        f"**Project:** {project_name}\n"
        f"**Description:** {project_description}\n"
        f"**Tech Stack:** {tech_stack}\n"
        f"**Features:** {features}\n\n"
        "Include these sections:\n"
        "- Title with badges\n"
        "- Description\n"
        "- Features list\n"
        "- Tech stack\n"
        "- Prerequisites\n"
        "- Quick Start / Installation\n"
        "- Usage with examples\n"
        "- Contributing\n"
        "- License\n\n"
        "Use proper Markdown formatting with code blocks where appropriate."
    )


# ─── Pattern 6: Meeting Summary Prompt ────────────────────────────────────────

@mcp.prompt()
def summarize_meeting(transcript: str, attendees: str = "") -> str:
    """
    Generate a structured meeting summary from a transcript.

    Args:
        transcript: The meeting transcript or notes.
        attendees: List of attendees (optional, comma-separated).
    """
    attendees_line = f"\nAttendees: {attendees}" if attendees else ""
    return (
        f"Please create a structured meeting summary from this transcript:{attendees_line}\n\n"
        f"**Transcript:**\n{transcript}\n\n"
        "Format the summary with these sections:\n"
        "## Meeting Summary\n"
        "**Date/Time:** [if mentioned]\n"
        "**Attendees:** [if mentioned]\n\n"
        "### Key Decisions\n"
        "[List major decisions made]\n\n"
        "### Action Items\n"
        "[List action items with owners and due dates if mentioned]\n\n"
        "### Discussion Points\n"
        "[Brief summary of main topics discussed]\n\n"
        "### Next Steps\n"
        "[What happens next]"
    )


if __name__ == "__main__":
    mcp.run()
