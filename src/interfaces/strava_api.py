from abc import ABC, abstractmethod
from typing import Any, Dict


class SyncStravaAPI(ABC):
    @abstractmethod
    def make_request(self, endpoint: str, params: dict = None) -> dict:
        pass


class AsyncStravaAPI(ABC):
    @abstractmethod
    async def make_request_async(
        self,
        endpoint: str,
        params: dict = None,
        *args,
    ) -> dict:
        pass


class HTTPClient(ABC):
    @abstractmethod
    def get(
        self, url: str, headers: Dict[str, str], params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        pass
