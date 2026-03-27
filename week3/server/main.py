"""MCP server entrypoint.

Starts a FastMCP server over STDIO by default.  The transport can be
swapped to SSE or Streamable HTTP by changing the ``run()`` call — no
tool or client code needs to change.
"""

from __future__ import annotations

import logging
import sys

from mcp.server.fastmcp import FastMCP

from .tools import weather, stocks


# ---------------------------------------------------------------------------
# Logging — write to stderr so STDIO transport stays clean.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "Weather & Finance MCP Server",
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
    """Run the server with STDIO transport (default)."""
    logger.info("Starting MCP server (STDIO transport)")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
