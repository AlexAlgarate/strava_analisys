from abc import ABC, abstractmethod
from typing import Any


class ValueFormatter(ABC):
    @abstractmethod
    def format(self, value: Any) -> str:
        pass
