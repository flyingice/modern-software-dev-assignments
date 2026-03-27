"""Yahoo Finance client — fetches real-time stock quotes via RapidAPI."""

from __future__ import annotations

import logging
from typing import Any

from .base import BaseClient
from ..config import settings


logger = logging.getLogger(__name__)


class YahooFinanceClient(BaseClient):
    """Wraps the Yahoo Finance RapidAPI (yahoo-finance15)."""

    def __init__(self) -> None:
        super().__init__()
        self.host = settings.yahoo_finance_host

    def get_quote(self, symbol: str) -> dict[str, Any]:
        """Return a quote summary for a single ticker symbol.

        Returns a flat dict with the most useful fields extracted from
        the upstream response so callers don't need to know the raw
        shape.
        """
        url = f"https://{self.host}/api/v1/markets/stock/quotes"
        data = self._get(url, params={"ticker": symbol})

        if not data or not data.get("body"):
            return {"error": f"No data returned for symbol '{symbol}'"}

        body = data["body"]
        if isinstance(body, list):
            if len(body) == 0:
                return {"error": f"No data returned for symbol '{symbol}'"}
            body = body[0]

        return {
            "symbol": body.get("symbol", symbol),
            "name": body.get("fullExchangeName", ""),
            "price": body.get("regularMarketPrice", "N/A"),
            "change": body.get("regularMarketChange", "N/A"),
            "change_percent": body.get("regularMarketChangePercent", "N/A"),
            "currency": body.get("currency", ""),
            "market_state": body.get("marketState", ""),
            "exchange": body.get("fullExchangeName", ""),
        }
