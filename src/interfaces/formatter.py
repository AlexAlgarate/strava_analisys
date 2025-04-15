from abc import ABC, abstractmethod
from typing import Any


class IValueFormatter(ABC):
    @abstractmethod
    def format(self, value: Any) -> str:
        pass
