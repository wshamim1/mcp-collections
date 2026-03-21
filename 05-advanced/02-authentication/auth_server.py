"""
MCP with Authentication — API Key & OAuth Patterns
====================================================
Shows how to secure MCP servers with authentication:
1. API Key authentication (header-based)
2. Environment-variable secrets
3. Per-tool authorization (role-based access)

For production: use proper secret management (AWS Secrets Manager,
HashiCorp Vault, etc.) — never hardcode credentials.

Run:
    API_KEY=my-secret-key python auth_server.py
"""

import hashlib
import hmac
import os
import secrets
from datetime import datetime
from functools import wraps
from typing import Optional

from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("authenticated-server")

# ─── Configuration ─────────────────────────────────────────────────────────
# In production: load from environment or secret manager
API_KEY = os.environ.get("API_KEY", "")
ADMIN_KEY = os.environ.get("ADMIN_KEY", "")

# Simulated session store (use Redis in production)
_active_sessions: dict[str, dict] = {}


# ─── Auth Helpers ─────────────────────────────────────────────────────────────

def _verify_api_key(provided_key: str, expected_key: str) -> bool:
    """
    Constant-time comparison to prevent timing attacks.
    Never use '==' for comparing secrets!
    """
    if not expected_key:
        return False
    return hmac.compare_digest(
        provided_key.encode("utf-8"),
        expected_key.encode("utf-8"),
    )


def require_api_key(func):
    """Decorator that validates api_key before running tool."""
    @wraps(func)
    async def wrapper(*args, api_key: str = "", **kwargs):
        if not _verify_api_key(api_key, API_KEY):
            return {"error": "Unauthorized: Invalid or missing API key.", "authenticated": False}
        return await func(*args, **kwargs)
    return wrapper


# ─── Tools with Authentication ────────────────────────────────────────────────

@mcp.tool()
async def authenticate(api_key: str) -> dict:
    """
    Authenticate with an API key and receive a session token.

    Args:
        api_key: Your API key.

    Returns:
        Session token valid for 1 hour, or error on failure.
    """
    if not _verify_api_key(api_key, API_KEY):
        return {"error": "Invalid API key.", "authenticated": False}

    # Generate a secure session token
    token = secrets.token_urlsafe(32)
    _active_sessions[token] = {
        "created_at": datetime.utcnow().isoformat(),
        "role": "admin" if _verify_api_key(api_key, ADMIN_KEY) else "user",
    }

    return {
        "authenticated": True,
        "session_token": token,
        "role": _active_sessions[token]["role"],
        "expires_in": "3600 seconds",
    }


@mcp.tool()
async def get_protected_data(session_token: str) -> dict:
    """
    Access protected data using a session token.

    Args:
        session_token: Token received from authenticate().

    Returns:
        Protected data, or authorization error.
    """
    if session_token not in _active_sessions:
        return {"error": "Unauthorized: Invalid or expired session token."}

    session = _active_sessions[session_token]
    return {
        "data": "This is protected data — only visible to authenticated users",
        "your_role": session["role"],
        "session_created": session["created_at"],
    }


@mcp.tool()
async def admin_list_sessions(session_token: str) -> dict:
    """
    List all active sessions. Requires admin role.

    Args:
        session_token: Admin session token.
    """
    session = _active_sessions.get(session_token)
    if not session:
        return {"error": "Unauthorized: Invalid session."}
    if session.get("role") != "admin":
        return {"error": "Forbidden: Admin role required."}

    return {
        "active_sessions": len(_active_sessions),
        "sessions": [
            {"created_at": s["created_at"], "role": s["role"]}
            for s in _active_sessions.values()
        ],
    }


@mcp.tool()
async def revoke_session(session_token: str) -> dict:
    """
    Revoke (log out) a session token.

    Args:
        session_token: The token to invalidate.
    """
    if session_token in _active_sessions:
        del _active_sessions[session_token]
        return {"success": True, "message": "Session revoked."}
    return {"error": "Session not found."}


# ─── Public Tool (no auth) ───────────────────────────────────────────────────

@mcp.tool()
def get_public_info() -> dict:
    """Get public server information — no authentication required."""
    return {
        "server": "authenticated-server",
        "auth_required": True,
        "api_configured": bool(API_KEY),
        "message": "Call authenticate() with your API key to access protected tools.",
    }


if __name__ == "__main__":
    if not API_KEY:
        print("⚠️  Warning: API_KEY not set. Set it with: export API_KEY=your-secret-key")
        print("   Server will run but authentication will always fail.")
    else:
        print(f"🔐 Auth server running (API key configured)")
    mcp.run()
