from abc import ABC, abstractmethod


class IDatabaseReader(ABC):
    @abstractmethod
    def fetch_latest_record(
        self, table: str, column: str, order_by: str | None = None
    ) -> dict[str, str] | None:
        pass
