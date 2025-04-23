from abc import ABC, abstractmethod
from typing import Dict


class IDatabaseWriter(ABC):
    @abstractmethod
    def insert_record(self, table: str, data: Dict[str, str | int]) -> bool:
        pass
