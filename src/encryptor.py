import logging
from datetime import datetime
from typing import Dict, Union

from cryptography.fernet import Fernet, InvalidToken

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class DataEncryptor:
    """Handles encryption and decryption of data using Fernet symmetric encryption."""

    def __init__(self, cipher: Fernet):
        """
        Initializes the DataEncryptor with a given cipher.

        Args:
            cipher (Fernet): An instance of the Fernet encryption class used for encryption/decryption.


        """
        self.cipher = cipher
        self.time_logger_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def encrypt_data(self, data: Dict[str, Union[str, int]]) -> Dict[str, str]:
        """
        Encrypts the given data dictionary.

        Args:
            data (Dict[str, Union[str, int]]): The data to be encrypted,
            where keys are strings and values are either strings or integers.

        Returns:
            Dict[str, str]: A dictionary with encrypted values as strings.

        Raises:
            ValueError: If encryption fails for any reason.
        """
        try:
            encrypted_data = {
                key: self.cipher.encrypt(str(value).encode()).decode()
                for key, value in data.items()
            }
            logger.info(f"Data encrypted successfully at {self.time_logger_now}")
            return encrypted_data
        except Exception as e:
            logger.error(f"Error encrypting data: {e}", exc_info=True)
            raise ValueError("Encryptation failed due to an error") from e

    def decrypt_data(
        self, data: Dict[str, Union[str, int]]
    ) -> Dict[str, Union[str, int]]:
        """
        Decrypts the given data dictionary.

        Args:
            data (Dict[str, Union[str, int]]): The data to be decrypted, where values are encrypted strings.

        Returns:
            Dict[str, Union[str, int]]: A dictionary with decrypted values.

        Raises:
            ValueError: If decryption fails for any reason.
        """
        try:
            decrypted_data = {}
            for key, value in data.items():
                if isinstance(value, str):
                    decrypted_data[key] = self.cipher.decrypt(value.encode()).decode()
                else:
                    decrypted_data[key] = value
            logger.info(f"Data decrypted successfully at {self.time_logger_now}")
            return decrypted_data

        except InvalidToken:
            logger.error("Decryption failed: invalid token detected.")
            raise ValueError("Decryption failed: invalid token detected.")

        except Exception as e:
            logger.error(f"Error decrypting data: {e}", exc_info=True)
            raise ValueError("Decryption failed due to an error.") from e

    def decrypt_value(
        self, data_to_decrypt: dict, value: str = "access_token"
    ) -> Union[str, int]:
        decrypted_data = self.decrypt_data(data_to_decrypt)
        return decrypted_data[value]
