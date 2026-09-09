from abc import ABC, abstractmethod
from typing import Any


class BaseASyncHTTPClient(ABC):
    @abstractmethod
    async def make_async_request(
        self,
        url: str,
        headers: dict[str, str],
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]: ...
