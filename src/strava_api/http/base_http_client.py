from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseHTTPClient(ABC):
    @abstractmethod
    def get_method(
        self, url: str, headers: Dict[str, str], params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        pass
