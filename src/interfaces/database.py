from abc import ABC, abstractmethod
from typing import Any, Dict, List, TypeVar, Union

T = TypeVar("T", bound=Dict[str, Any])


class DatabaseReaderInterface(ABC):
    @abstractmethod
    def fetch_latest_record(
        self, table: str, column: str, order_by: str | None = None
    ) -> T | None:
        pass


class DatabaseWriterInterface(ABC):
    @abstractmethod
    def insert_record(self, table: str, data: Dict[str, Union[str, int]]) -> bool:
        pass


class DatabaseDeleterInterface(ABC):
    @abstractmethod
    def delete_record(self, table: str, record: List[int]) -> bool:
        pass
