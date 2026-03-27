"""MCP tool definitions for current weather."""

from __future__ import annotations

import json
import logging
import re

from pydantic import BaseModel, field_validator

from mcp.server.fastmcp import FastMCP

from ..clients.weatherapi import WeatherAPIClient
from ..clients.base import APIError, RateLimitError


logger = logging.getLogger(__name__)

_client = WeatherAPIClient()

# Matches a lat/lon pair like "48.8567,2.3508" or "-33.87,151.21".
_LATLON_RE = re.compile(
    r"^-?\d{1,3}(\.\d+)?\s*,\s*-?\d{1,3}(\.\d+)?$"
)

# Matches a reasonable city name: letters, spaces, hyphens, apostrophes, dots.
_CITY_RE = re.compile(r"^[\w\s.'\-]{1,100}$", re.UNICODE)


class WeatherInput(BaseModel):
    """Validated input for the get_weather tool."""

    city: str

    @field_validator("city")
    @classmethod
    def validate_city(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("City must not be empty.")
        if _LATLON_RE.match(v):
            return v
        if not _CITY_RE.match(v):
            raise ValueError(
                f"Invalid city '{v}'. "
                "Expected a city name or lat,lon pair (e.g. '48.8567,2.3508')."
            )
        return v


def register(mcp: FastMCP) -> None:
    """Register weather-related tools on the given MCP server."""

    @mcp.tool()
    def get_weather(city: str) -> str:
        """Get current weather for a city.

        Args:
            city: City name (e.g. "London", "New York")
                or lat/lon pair ("48.8567,2.3508").

        Returns:
            JSON object with temperature, conditions, humidity, wind,
            and other weather details.
        """
        logger.info("get_weather called with city=%s", city)
        try:
            validated = WeatherInput(city=city)
            result = _client.get_current_weather(validated.city)
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
            logger.exception("unexpected error in get_weather")
            return json.dumps({"error": str(exc)})
