"""from unittest.mock import Mock, patch

import pytest

from src.access_token import GetAccessToken


@pytest.fixture
def mock_logger():
    return Mock()


@pytest.fixture
def mock_credentials():
    return {
        "supabase_secrets": Mock(),
        "strava_secrets": Mock(),
        "fernet_secrets": Mock(),
    }


class TestGetAccessToken:
    @pytest.fixture
    def token_manager(self, mock_logger, mock_credentials):
        with patch.object(GetAccessToken, "_load_credentials") as mock_load:
            mock_load.return_value = mock_credentials
            manager = GetAccessToken(logger=mock_logger)
            return manager

    def test_initialization(self, token_manager, mock_credentials):
        assert token_manager.credentials == mock_credentials
        assert hasattr(token_manager, "supabase_client")
        assert hasattr(token_manager, "supabase_reader")
        assert hasattr(token_manager, "supabase_writer")
        assert hasattr(token_manager, "supabase_deleter")
        assert hasattr(token_manager, "token_manager")
        assert hasattr(token_manager, "encryptor")
        assert hasattr(token_manager, "token_handler")

    @patch("supabase.create_client")
    def test_create_supabase_client(self, mock_create_client, token_manager):
        token_manager._create_supabase_client()
        mock_create_client.assert_called_once()

    def test_load_credentials(self):
        with patch("dotenv.load_dotenv") as mock_load_dotenv:
            manager = GetAccessToken(logger=Mock())
            credentials = manager._load_credentials()

            mock_load_dotenv.assert_called_once()
            assert "supabase_secrets" in credentials
            assert "strava_secrets" in credentials
            assert "fernet_secrets" in credentials

    def test_get_access_token(self, token_manager):
        # Mock the necessary components
        mock_table = "test_table"
        token_manager.credentials["supabase_secrets"].SUPABASE_TABLE = mock_table

        mock_token = {"access_token": "encrypted_token"}
        token_manager.supabase_reader.fetch_latest_record.return_value = mock_token

        token_manager.encryptor.decrypt_value.return_value = "decrypted_token"

        # Call the method
        result = token_manager.get_access_token()

        # Verify the interactions
        token_manager.token_handler.process_token.assert_called_once_with(mock_table)
        token_manager.supabase_reader.fetch_latest_record.assert_called_once_with(
            mock_table, "access_token", "access_token"
        )
        token_manager.encryptor.decrypt_value.assert_called_once_with(
            data_to_decrypt=mock_token, value="access_token"
        )
        assert result == "decrypted_token"

    def test_create_components(self, token_manager):
        # Test creation of supabase components
        assert token_manager._create_supabase_reader() is not None
        assert token_manager._create_supabase_writer() is not None
        assert token_manager._create_supabase_deleter() is not None

        # Test creation of other components
        assert token_manager._create_token_manager() is not None
        assert token_manager._create_encryptor() is not None
        assert token_manager._create_token_handler() is not None
"""
