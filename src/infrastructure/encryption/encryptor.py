import logging
from typing import Dict

from cryptography.fernet import Fernet

from src.interfaces.encryption.encryptor import IEncryptation

logger = logging.getLogger(__name__)


class FernetEncryptor(IEncryptation):
    def __init__(self, cipher: Fernet):
        if not isinstance(cipher, Fernet):
            raise ValueError("Cipher must be an instance of Fernet.")
        self.cipher = cipher

    def encrypt_data(self, data: Dict[str, str | int]) -> Dict[str, str]:
        try:
            encrypted_data = {
                key: self.cipher.encrypt(str(value).encode()).decode()
                for key, value in data.items()
            }
            logger.info("Data encrypted successfully.")
            return encrypted_data

        except Exception as e:
            logger.error(f"Error encrypting data: {e}", exc_info=True)
            raise ValueError("Encryptation failed due to an error") from e

    def decrypt_data(self, data: Dict[str, str]) -> Dict[str, str]:
        try:
            decrypted_data = {
                key: (
                    self.cipher.decrypt(value.encode()).decode()
                    if isinstance(value, str)
                    else value
                )
                for key, value in data.items()
            }
            logger.info("Data decrypted successfully.")
            return decrypted_data

        except Exception as e:
            logger.error(f"Error decrypting data: {e}", exc_info=True)
            raise ValueError("Decryption failed due to an error.") from e

    def decrypt_value(
        self, data_to_decrypt: Dict[str, str], value: str
    ) -> str | int:
        try:
            decrypted_data = self.decrypt_data(data_to_decrypt)
            return decrypted_data[value]
        except Exception as e:
            logger.error(f"Error decripting the value: {e}", exc_info=True)
            raise KeyError(
                f"Decryption failed, {decrypted_data[value]} doesn't exist."
            ) from e
