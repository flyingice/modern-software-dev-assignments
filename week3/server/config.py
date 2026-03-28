"""Configuration module — loads settings from environment variables."""

import os
import logging


logger = logging.getLogger(__name__)


class Settings:
    """Application settings populated from environment variables.

    Centralises all external configuration so the rest of the codebase
    never reads os.environ directly.  A future OAuth 2.0 layer can
    extend this class with token-endpoint URLs and client credentials
    without touching any other module.
    """

    def __init__(self) -> None:
        self.rapidapi_key: str = os.environ.get("RAPIDAPI_KEY", "")
        self.yahoo_finance_host: str = os.environ.get(
            "YAHOO_FINANCE_HOST", "yahoo-finance15.p.rapidapi.com"
        )
        self.weatherapi_host: str = os.environ.get(
            "WEATHERAPI_HOST", "weatherapi-com.p.rapidapi.com"
        )
        self.request_timeout: float = float(
            os.environ.get("REQUEST_TIMEOUT", "10")
        )
        self.server_host: str = os.environ.get("FASTMCP_HOST", "0.0.0.0")
        self.server_port: int = int(os.environ.get("FASTMCP_PORT", "8000"))

        if not self.rapidapi_key:
            logger.warning(
                "RAPIDAPI_KEY is not set — API calls will fail. "
                "Export the variable before starting the server."
            )


settings = Settings()
