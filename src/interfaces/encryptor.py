from abc import ABC, abstractmethod
from typing import Dict


class IEncryptation(ABC):
    @abstractmethod
    def encrypt_data(self, data: Dict[str, str | int]) -> Dict[str, str]:
        pass

    @abstractmethod
    def decrypt_data(self, data: Dict[str, int | str]) -> Dict[str, int | str]:
        pass

    @abstractmethod
    def decrypt_value(
        self, data_to_decrypt: Dict[str, int | str], value: str
    ) -> str | int: ...
