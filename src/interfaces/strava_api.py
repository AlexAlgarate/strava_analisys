"""Strava API interfaces."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class HTTPClient(ABC):
    """Base interface for HTTP clients."""

    @abstractmethod
    def get(
        self, url: str, headers: Dict[str, str], params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make a GET request to the specified URL."""
        pass


class BaseStravaAPI(ABC):
    """Base interface for Strava API implementations."""

    @abstractmethod
    def __init__(self, access_token: str, http_client: HTTPClient, config: Any = None):
        """Initialize with required dependencies."""
        pass

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """Get headers for Strava API requests."""
        pass

    @abstractmethod
    def get_url(self, endpoint: str) -> str:
        """Get full URL for Strava API endpoint."""
        pass
