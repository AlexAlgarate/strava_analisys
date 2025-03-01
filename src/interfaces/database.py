from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, Union

T = TypeVar("T", bound=Dict[str, Any])


class DatabaseReaderInterface(ABC):
    @abstractmethod
    def fetch_latest_record(
        self, table: str, column: str, order_by: Optional[str] = None
    ) -> Optional[T]:
        pass


class DatabaseWriterInterface(ABC):
    @abstractmethod
    def insert_record(self, table: str, data: Dict[str, Union[str, int]]) -> bool:
        pass
