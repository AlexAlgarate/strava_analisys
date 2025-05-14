from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict

from .async_http_client import BaseASyncHTTPClient


@dataclass
class StravaAPIConfig:
    base_url: str = "https://www.strava.com/api/v3"
    content_type: str = "application/json"


class BaseStravaAPI(ABC):
    def __init__(
        self,
        access_token: str,
        http_client: BaseASyncHTTPClient,
        config: StravaAPIConfig | None = None,
    ):
        if not access_token:
            raise ValueError("\n\nAccess token must be provided.")
        self.access_token = access_token
        self.http_client = http_client
        self.config = config or StravaAPIConfig()

    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": self.config.content_type,
        }

    def get_url(self, endpoint: str) -> str:
        return f"{self.config.base_url}{endpoint}"

    @abstractmethod
    def make_request(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> Any: ...
