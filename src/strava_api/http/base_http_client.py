"""Base HTTP client interface and implementations."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseHTTPClient(ABC):
    """Base interface for HTTP clients."""

    @abstractmethod
    def get(
        self, url: str, headers: Dict[str, str], params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make a GET request to the specified URL."""
        pass
