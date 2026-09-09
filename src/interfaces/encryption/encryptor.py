from abc import ABC, abstractmethod


class IEncryptation(ABC):
    @abstractmethod
    def encrypt_data(self, data: dict[str, str | int]) -> dict[str, str]:
        pass

    @abstractmethod
    def decrypt_data(self, data: dict[str, str]) -> dict[str, str]:
        pass

    @abstractmethod
    def decrypt_value(
        self, data_to_decrypt: dict[str, str], value: str
    ) -> str | int: ...
