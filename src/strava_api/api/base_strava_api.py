"""Base class for Strava API implementations."""

from abc import ABC
from dataclasses import dataclass
from typing import Dict

from ..http.base_http_client import BaseHTTPClient


@dataclass
class StravaAPIConfig:
    """Configuration for Strava API."""

    base_url: str = "https://www.strava.com/api/v3"
    content_type: str = "application/json"


class BaseStravaAPI(ABC):
    """Base class for Strava API implementations."""

    def __init__(
        self,
        access_token: str,
        http_client: BaseHTTPClient,
        config: StravaAPIConfig = None,
    ):
        if not access_token:
            raise ValueError("\n\nAccess token must be provided.")
        self.access_token = access_token
        self.http_client = http_client
        self.config = config or StravaAPIConfig()

    def get_headers(self) -> Dict[str, str]:
        """Get headers for Strava API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": self.config.content_type,
        }

    def get_url(self, endpoint: str) -> str:
        """Get full URL for Strava API endpoint."""
        return f"{self.config.base_url}{endpoint}"
