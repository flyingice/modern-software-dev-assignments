"""MCP tool definitions for stock quotes."""

from __future__ import annotations

import json
import logging
import re

from pydantic import BaseModel, field_validator

from mcp.server.fastmcp import FastMCP

from ..clients.base import APIError, RateLimitError
from ..clients.yahoo_finance import YahooFinanceClient


logger = logging.getLogger(__name__)

_client = YahooFinanceClient()

# Matches standard ticker symbols: 1-5 uppercase letters, optional dot suffix
# (e.g. AAPL, BRK.B, TSM).
_TICKER_RE = re.compile(r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$")


class StockQuoteInput(BaseModel):
    """Validated input for the get_stock_quote tool."""

    symbol: str

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        v = v.strip().upper()
        if not _TICKER_RE.match(v):
            raise ValueError(
                f"Invalid ticker symbol '{v}'. "
                "Expected 1-5 letters, optional dot suffix (e.g. AAPL, BRK.B)."
            )
        return v


def register(mcp: FastMCP) -> None:
    """Register stock-related tools on the given MCP server."""

    @mcp.tool()
    def get_stock_quote(symbol: str) -> str:
        """Get a real-time stock quote for a given ticker symbol.

        Args:
            symbol: A stock ticker symbol such as AAPL, MSFT, or TSLA.

        Returns:
            JSON string with price, change, percent change, and market
            state for the requested symbol.
        """
        logger.info("get_stock_quote called with symbol=%s", symbol)
        try:
            validated = StockQuoteInput(symbol=symbol)
            result = _client.get_quote(validated.symbol)
            return json.dumps(result, indent=2)
        except RateLimitError as exc:
            logger.warning("rate limited: %s", exc)
            return json.dumps({
                "error": "Rate limit reached. Please wait and try again.",
                "retry_after_seconds": exc.retry_after,
            })
        except APIError as exc:
            logger.error("API error: %s", exc)
            return json.dumps({
                "error": f"Upstream API error: {exc.detail}",
                "status_code": exc.status_code,
            })
        except ValueError as exc:
            logger.warning("validation error: %s", exc)
            return json.dumps({"error": str(exc)})
        except Exception as exc:
            logger.exception("unexpected error in get_stock_quote")
            return json.dumps({"error": str(exc)})
