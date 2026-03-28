"""MCP server entrypoint.

Starts a FastMCP server over Streamable HTTP on localhost.  The host and
port are configured via FASTMCP_HOST / FASTMCP_PORT environment variables
(defaults: 0.0.0.0:8000).
"""

from __future__ import annotations

import logging
import sys

from mcp.server.auth.settings import (
    AuthSettings,
    ClientRegistrationOptions,
    RevocationOptions,
)
from mcp.server.fastmcp import FastMCP

from .auth import InMemoryOAuthProvider
from .config import settings
from .tools import weather, stocks


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# OAuth (optional, controlled by OAUTH_ENABLED env var)
# ---------------------------------------------------------------------------
auth_provider = None
auth_settings = None

if settings.oauth_enabled:
    auth_provider = InMemoryOAuthProvider()
    auth_settings = AuthSettings(
        issuer_url=settings.oauth_issuer_url,
        resource_server_url=settings.oauth_issuer_url,
        required_scopes=settings.oauth_required_scopes or None,
        client_registration_options=ClientRegistrationOptions(
            enabled=True,
            valid_scopes=["read", "write"],
            default_scopes=["read"],
        ),
        revocation_options=RevocationOptions(enabled=True),
    )

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "Weather & Finance MCP Server",
    host=settings.server_host,
    port=settings.server_port,
    auth_server_provider=auth_provider,
    auth=auth_settings,
    instructions=(
        "This server provides two tools:\n"
        "1. get_stock_quote — real-time stock price via Yahoo Finance\n"
        "2. get_weather — current weather conditions via WeatherAPI.com\n"
        "Both require a RAPIDAPI_KEY environment variable."
    ),
)

# Register tool modules.
stocks.register(mcp)
weather.register(mcp)


def main() -> None:
    """Run the server with Streamable HTTP transport."""
    logger.info(
        "Starting MCP server (Streamable HTTP on %s:%s)",
        settings.server_host,
        settings.server_port,
    )
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
