from abc import ABC, abstractmethod
from typing import Any, Dict, List, TypeVar

T = TypeVar("T", bound=Dict[str, Any])


class DatabaseReaderInterface(ABC):
    @abstractmethod
    def fetch_latest_record(
        self, table: str, column: str, order_by: str | None = None
    ) -> T | None:
        pass


class DatabaseWriterInterface(ABC):
    @abstractmethod
    def insert_record(self, table: str, data: Dict[str, str | int]) -> bool:
        pass


class DatabaseDeleterInterface(ABC):
    @abstractmethod
    def delete_records(self, table: str, ids_to_delete: List[int]) -> bool:
        pass

    @abstractmethod
    def get_expired_token_ids(self, table: str, encryptor) -> List[int]:
        pass

    @abstractmethod
    def cleanup_expired_tokens(self, table: str, encryptor) -> bool:
        pass
