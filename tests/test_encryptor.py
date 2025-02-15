from typing import Union
from unittest.mock import patch

import pytest
from cryptography.fernet import Fernet

from src.encryptor import DataEncryptor


class TestEncryptor:
    @pytest.fixture
    def cipher(self):
        return Fernet(Fernet.generate_key())

    @pytest.fixture
    def encryptor(self, cipher):
        return DataEncryptor(cipher)

    @pytest.fixture
    def sample_data(self):
        return {
            "access_token": "qwerty12345",
            "refresh_token": "12345qwerty",
            "expires_at": 1738222356,
            "access_token_creation": "2025-01-30 08:40:21",
        }

    def test_init_with_valid_cipher(self, cipher):
        encryptor = DataEncryptor(cipher)
        assert isinstance(encryptor.cipher, Fernet)

    def test_init_with_invalid_cipher(self):
        with pytest.raises(ValueError, match="Cipher must be an instance of Fernet."):
            DataEncryptor("invalid_cipher")

    def test_encrypt_data(self, encryptor, sample_data):
        encrypted_data = encryptor.encrypt_data(sample_data)

        assert isinstance(encrypted_data, dict)
        assert set(encrypted_data.keys()) == set(sample_data.keys())

        for value in encrypted_data.values():
            assert isinstance(value, Union[str, int])
            assert value not in sample_data.values()

    def test_encrypt_data_with_empty_dict(self, encryptor):
        encrypted_data = encryptor.encrypt_data({})
        assert encrypted_data == {}

    @patch("src.utils.Logger.setup_logger")
    def test_encrypt_data_error(self, mock_logger, encryptor):
        invalid_data = {"key": object()}

        with pytest.raises(ValueError, match="Encryptation failed due to an error"):
            encryptor.encrypt_data(invalid_data)

    def test_decrypt_data_success(self, encryptor, sample_data):
        encrypted_data = encryptor.encrypt_data(sample_data)

        decrypted_data = encryptor.decrypt_data(encrypted_data)
        decrypted_data["expires_at"] = int(decrypted_data["expires_at"])

        assert decrypted_data == sample_data
        assert all(isinstance(value, (str, int)) for value in decrypted_data.values())

    def test_decrypt_data_with_mixed_values(self, encryptor, sample_data):
        encrypted_data = encryptor.encrypt_data(sample_data)

        mixed_data = {
            "access_token": encrypted_data["access_token"],
            "refresh_token": 30,
            "expires_at": encrypted_data["expires_at"],
            "access_token_creation": encrypted_data["access_token_creation"],
        }

        decrypted_data = encryptor.decrypt_data(mixed_data)
        assert decrypted_data["access_token"] == "qwerty12345"
        assert decrypted_data["refresh_token"] == 30
        assert decrypted_data["expires_at"] == "1738222356"
        assert decrypted_data["access_token_creation"] == "2025-01-30 08:40:21"

    def test_decrypt_data_invalid_token(self, encryptor):
        invalid_data = {"key": "invalid_encrypted_value"}

        with pytest.raises(
            ValueError, match="Decryption failed: invalid token detected."
        ):
            encryptor.decrypt_data(invalid_data)

    def test_decrypt_one_value_successfully(self, encryptor, sample_data):
        encrypted_data = encryptor.encrypt_data(sample_data)

        decrypted_access_token = encryptor.decrypt_value(encrypted_data, "access_token")
        assert decrypted_access_token == sample_data["access_token"]

        decrypted_int_expires_at = encryptor.decrypt_value(encrypted_data, "expires_at")
        assert decrypted_int_expires_at == str(sample_data["expires_at"])

    def test_decrypt_one_value_key_error(self, encryptor, sample_data):
        encrypted_data = encryptor.encrypt_data(sample_data)

        with pytest.raises(KeyError):
            encryptor.decrypt_value(encrypted_data, "non_existent_key")

    def test_large_data_handling(self, encryptor):
        large_data = {f"key_{i}": f"value_{i}" for i in range(10000)}
        encrypted = encryptor.encrypt_data(large_data)
        decrypted = encryptor.decrypt_data(encrypted)
        assert decrypted == large_data
