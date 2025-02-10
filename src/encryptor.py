from typing import Dict, Union

from cryptography.fernet import Fernet, InvalidToken

from src import utils as utils


class DataEncryptor:
    """Handles encryption and decryption of data using Fernet symmetric encryption."""

    def __init__(self, cipher: Fernet):
        """
        Initializes the DataEncryptor with a given cipher.

        Args:
            cipher (Fernet): An instance of the Fernet encryption class used for encryption/decryption.
        """

        if not isinstance(cipher, Fernet):
            raise ValueError("Cipher must be an instance of Fernet.")
        self.cipher = cipher
        self.logger = utils.Logger().setup_logger()

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
            encrypted_data = {}
            for key, value in data.items():
                if not isinstance(value, (str, int)):
                    raise ValueError(f"Invalid data type for {key}: {type(value)}")
                encrypted_data[key] = self.cipher.encrypt(str(value).encode()).decode()
            self.logger.info("Data encrypted successfully.")
            return encrypted_data

        except Exception as e:
            self.logger.error(f"Error encrypting data: {e}", exc_info=True)
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

        except InvalidToken:
            self.logger.error("Decryption failed: invalid token detected.")
            raise ValueError("Decryption failed: invalid token detected.")

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
