from typing import Dict, Union

from cryptography.fernet import Fernet

from src.interfaces.encryptor import EncryptationInterface
from src.utils.logging import Logger


class FernetEncryptor(EncryptationInterface):
    def __init__(self, cipher: Fernet, logger: Logger):
        if not isinstance(cipher, Fernet):
            raise ValueError("Cipher must be an instance of Fernet.")
        self.cipher = cipher
        self.logger = logger

    def encrypt_data(self, data: Dict[str, Union[str, int]]) -> Dict[str, str]:
        try:
            encrypted_data = {
                key: self.cipher.encrypt(str(value).encode()).decode()
                for key, value in data.items()
            }
            self.logger.info("Data encrypted successfully.")
            return encrypted_data

        except Exception as e:
            self.logger.error(f"Error encrypting data: {e}", exc_info=True)
            raise ValueError("Encryptation failed due to an error") from e

    def decrypt_data(
        self, data: Dict[str, Union[str, int]]
    ) -> Dict[str, Union[str, int]]:
        try:
            decrypted_data = {
                key: (
                    self.cipher.decrypt(value.encode()).decode()
                    if isinstance(value, str)
                    else value
                )
                for key, value in data.items()
            }
            self.logger.info("Data decrypted successfully.")
            return decrypted_data

        except Exception as e:
            self.logger.error(f"Error decrypting data: {e}", exc_info=True)
            raise ValueError("Decryption failed due to an error.") from e

    def decrypt_value(self, data_to_decrypt: dict, value: str) -> Union[str, int]:
        try:
            decrypted_data = self.decrypt_data(data_to_decrypt)
            return decrypted_data[value]
        except Exception as e:
            self.logger.error(f"Error decripting the value: {e}", exc_info=True)
            raise KeyError(
                f"Decryption failed, {decrypted_data[value]} doesn't exist."
            ) from e
