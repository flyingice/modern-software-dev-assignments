"""WeatherAPI.com client — fetches current weather via RapidAPI."""

from __future__ import annotations

import logging
from typing import Any

from .base import BaseClient
from ..config import settings


logger = logging.getLogger(__name__)


class WeatherAPIClient(BaseClient):
    """Wraps the WeatherAPI.com RapidAPI endpoint."""

    def __init__(self) -> None:
        super().__init__()
        self.host = settings.weatherapi_host

    def get_current_weather(self, city: str) -> dict[str, Any]:
        """Return current weather conditions for *city*.

        Parameters
        ----------
        city:
            City name (e.g. ``"London"``) or lat/lon pair
            (``"48.8567,2.3508"``).
        """
        url = f"https://{self.host}/current.json"
        params: dict[str, Any] = {"q": city}

        data = self._get(url, params=params)

        location = data.get("location", {})
        current = data.get("current", {})
        condition = current.get("condition", {})

        return {
            "city": location.get("name", ""),
            "region": location.get("region", ""),
            "country": location.get("country", ""),
            "local_time": location.get("localtime", ""),
            "temperature_c": current.get("temp_c"),
            "temperature_f": current.get("temp_f"),
            "feels_like_c": current.get("feelslike_c"),
            "feels_like_f": current.get("feelslike_f"),
            "condition": condition.get("text", ""),
            "humidity": current.get("humidity"),
            "wind_mph": current.get("wind_mph"),
            "wind_kph": current.get("wind_kph"),
            "wind_direction": current.get("wind_dir", ""),
            "wind_degree": current.get("wind_degree"),
            "gust_mph": current.get("gust_mph"),
            "gust_kph": current.get("gust_kph"),
            "pressure_mb": current.get("pressure_mb"),
            "pressure_in": current.get("pressure_in"),
            "precip_mm": current.get("precip_mm"),
            "precip_in": current.get("precip_in"),
            "visibility_km": current.get("vis_km"),
            "visibility_miles": current.get("vis_miles"),
            "cloudiness_pct": current.get("cloud"),
            "uv_index": current.get("uv"),
        }
