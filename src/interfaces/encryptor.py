from abc import ABC, abstractmethod
from typing import Dict, Union


class EncryptationInterface(ABC):
    @abstractmethod
    def encrypt_data(self, data: Dict[str, Union[str, int]]) -> Dict[str, str]:
        pass

    @abstractmethod
    def decrypt_data(self, data: Dict[str, str]) -> Dict[str, Union[str, int]]:
        pass

    @abstractmethod
    def decrypt_value(self, data_to_decrypt: dict, value: str) -> Union[str, int]: ...
