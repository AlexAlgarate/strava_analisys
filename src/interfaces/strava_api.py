from abc import ABC, abstractmethod
from typing import Any, Dict


class HTTPClient(ABC):
    @abstractmethod
    def get(
        self, url: str, headers: Dict[str, str], params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        pass


class BaseStravaAPI(ABC):
    @abstractmethod
    def __init__(self, access_token: str, http_client: HTTPClient, config: Any = None):
        pass

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def get_url(self, endpoint: str) -> str:
        pass
