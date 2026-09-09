from abc import ABC, abstractmethod


class IDatabaseWriter(ABC):
    @abstractmethod
    def insert_record(self, table: str, data: dict[str, str]) -> bool:
        pass
