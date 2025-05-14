from abc import ABC, abstractmethod
from typing import List

from src.interfaces.encryption.encryptor import IEncryptation


class IDatabaseDeleter(ABC):
    @abstractmethod
    def delete_records(self, table: str, ids_to_delete: List[int]) -> bool:
        pass

    @abstractmethod
    def get_expired_token_ids(self, table: str, encryptor: IEncryptation) -> List[int]:
        pass

    @abstractmethod
    def cleanup_expired_tokens(self, table: str, encryptor: IEncryptation) -> bool:
        pass
