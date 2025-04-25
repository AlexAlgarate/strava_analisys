from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseASyncHTTPClient(ABC):
    @abstractmethod
    async def get_method(
        self, url: str, headers: Dict[str, str], params: Dict[str, Any] = None
    ) -> Dict[str, Any]: ...
