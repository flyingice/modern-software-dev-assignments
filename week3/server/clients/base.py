"""Base HTTP client with retry, timeout, and rate-limit handling."""

from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from ..config import settings


logger = logging.getLogger(__name__)

# Simple in-memory rate-limit tracker keyed by host.
_rate_limit_until: dict[str, float] = {}


class APIError(Exception):
    """Raised when an upstream API returns a non-success response."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP {status_code}: {detail}")


class RateLimitError(APIError):
    """Raised specifically for 429 responses."""

    def __init__(self, retry_after: float, detail: str) -> None:
        self.retry_after = retry_after
        super().__init__(429, detail)


class BaseClient:
    """Thin wrapper around httpx providing RapidAPI-aware defaults.

    Subclasses set ``host`` and call ``_get`` / ``_post``.  The base
    class handles headers, timeouts, retries, and rate-limit back-off
    so that each integration only contains domain logic.

    The design keeps authentication concerns (currently a static API
    key) in a single place.  Swapping to an OAuth 2.0 bearer token
    later means changing only the ``_headers`` property — no other
    module is affected.
    """

    host: str = ""
    max_retries: int = 2
    retry_backoff: float = 1.0  # seconds, doubled on each retry

    def __init__(self) -> None:
        self._client = httpx.Client(timeout=settings.request_timeout)

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "x-rapidapi-key": settings.rapidapi_key,
            "x-rapidapi-host": self.host,
        }

    def _request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Execute an HTTP request with retry and rate-limit logic."""
        now = time.monotonic()
        blocked_until = _rate_limit_until.get(self.host, 0)
        if now < blocked_until:
            wait = blocked_until - now
            raise RateLimitError(
                wait,
                f"Rate-limited — retry after {wait:.1f}s",
            )

        backoff = self.retry_backoff
        last_exc: Exception | None = None

        for attempt in range(1, self.max_retries + 2):
            try:
                logger.debug(
                    "request attempt=%d %s %s params=%s",
                    attempt, method, url, params,
                )
                resp = self._client.request(
                    method, url, headers=self._headers, params=params,
                )

                if resp.status_code == 429:
                    retry_after = float(
                        resp.headers.get("Retry-After", backoff)
                    )
                    _rate_limit_until[self.host] = (
                        time.monotonic() + retry_after
                    )
                    raise RateLimitError(retry_after, resp.text)

                if resp.status_code >= 500:
                    raise APIError(resp.status_code, resp.text)

                resp.raise_for_status()
                return resp.json()

            except (httpx.TimeoutException, httpx.ConnectError) as exc:
                last_exc = exc
                logger.warning(
                    "transient error on attempt %d: %s", attempt, exc,
                )
            except RateLimitError:
                raise
            except APIError as exc:
                last_exc = exc
                logger.warning(
                    "server error on attempt %d: %s", attempt, exc,
                )

            if attempt <= self.max_retries:
                time.sleep(backoff)
                backoff *= 2

        raise last_exc or RuntimeError("request failed")

    def _get(
        self, url: str, *, params: dict[str, Any] | None = None,
    ) -> Any:
        return self._request("GET", url, params=params)
