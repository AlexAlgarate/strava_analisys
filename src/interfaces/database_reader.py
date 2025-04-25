from abc import ABC, abstractmethod
from typing import Dict

from src.utils import types as types


class IDatabaseReader(ABC):
    @abstractmethod
    def fetch_latest_record(
        self, table: str, column: str, order_by: str | None = None
    ) -> Dict[str, str | int] | None:
        pass
