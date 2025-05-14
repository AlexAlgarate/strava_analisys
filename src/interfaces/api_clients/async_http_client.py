from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseASyncHTTPClient(ABC):
    @abstractmethod
    async def make_async_request(
        self, url: str, headers: Dict[str, str], params: Dict[str, Any] | None = None
    ) -> Dict[str, Any]: ...
