from unittest.mock import Mock, patch

import pytest

from src.token_handler import TokenHandler
from src.utils import exceptions


@pytest.fixture
def mock_supabase_reader():
    return Mock()


@pytest.fixture
def mock_supabase_writer():
    return Mock()


@pytest.fixture
def mock_supabase_deleter():
    return Mock()


@pytest.fixture
def mock_token_manager():
    return Mock()


@pytest.fixture
def mock_encryptor():
    return Mock()


@pytest.fixture
def token_handler(
    mock_supabase_reader,
    mock_supabase_writer,
    mock_supabase_deleter,
    mock_token_manager,
    mock_encryptor,
):
    return TokenHandler(
        supabase_reader=mock_supabase_reader,
        supabase_writer=mock_supabase_writer,
        supabase_deleter=mock_supabase_deleter,
        token_manager=mock_token_manager,
        encryptor=mock_encryptor,
        client_id="test_client_id",
    )


class TestTokenHandler:
    def test_process_token_no_existing_record(
        self, token_handler, mock_supabase_reader
    ):
        mock_supabase_reader.fetch_latest_record.return_value = None
        with patch.object(token_handler, "_handle_initial_token_flow") as mock_initial:
            token_handler.process_token("test_table")
            mock_initial.assert_called_once_with("test_table")

    def test_process_token_with_existing_record(
        self, token_handler, mock_supabase_reader
    ):
        mock_record = {"access_token": "test_token"}
        mock_supabase_reader.fetch_latest_record.return_value = mock_record
        with patch.object(token_handler, "_handle_exisiting_token") as mock_existing:
            token_handler.process_token("test_table")
            mock_existing.assert_called_once_with(mock_record, "test_table")

    def test_handle_existing_token_expired(
        self, token_handler, mock_token_manager, mock_encryptor
    ):
        mock_record = {"access_token": "encrypted_token"}
        mock_encryptor.decrypt_data.return_value = {
            "expires_at": "1000",  # Expired timestamp
            "refresh_token": "test_refresh",
        }
        mock_token_manager.token_has_expired.return_value = True

        with patch.object(token_handler, "_refresh_and_store_token") as mock_refresh:
            token_handler._handle_exisiting_token(mock_record, "test_table")
            mock_refresh.assert_called_once_with("test_refresh", "test_table")

    def test_handle_existing_token_valid(
        self, token_handler, mock_token_manager, mock_encryptor
    ):
        mock_record = {"access_token": "encrypted_token"}
        decrypted_data = {
            "expires_at": "9999999999",  # Future timestamp
            "access_token": "test_token",
        }
        mock_encryptor.decrypt_data.return_value = decrypted_data
        mock_token_manager.token_has_expired.return_value = False

        result = token_handler._handle_exisiting_token(mock_record, "test_table")
        assert result == decrypted_data

    # @patch("src.oauth_code.GetOauthCode")
    # def test_handle_initial_token_flow_success(
    #     self, mock_oauth_code, token_handler, mock_token_manager
    # ):
    #     mock_oauth_code.return_value.get_authorization_code.return_value = "test_code"
    #     mock_token_manager.get_initial_tokens.return_value = {
    #         "access_token": "new_token",
    #         "refresh_token": "new_refresh",
    #         "expires_at": "9999999999",
    #     }

    #     with patch.object(token_handler, "_store_and_return_tokens") as mock_store:
    #         token_handler._handle_initial_token_flow("test_table")
    #         mock_store.assert_called_once()

    def test_refresh_and_store_token_success(self, token_handler, mock_token_manager):
        new_tokens = {
            "access_token": "new_token",
            "refresh_token": "new_refresh",
            "expires_at": "9999999999",
        }
        mock_token_manager.refresh_access_token.return_value = new_tokens

        with patch.object(token_handler, "_store_and_return_tokens") as mock_store:
            token_handler._refresh_and_store_token("old_refresh", "test_table")
            mock_store.assert_called_once_with(new_tokens, "test_table")

    def test_refresh_and_store_token_failure(self, token_handler, mock_token_manager):
        mock_token_manager.refresh_access_token.return_value = None

        with pytest.raises(exceptions.TokenError):
            token_handler._refresh_and_store_token("old_refresh", "test_table")

    def test_store_and_return_tokens_success(
        self, token_handler, mock_encryptor, mock_supabase_writer
    ):
        tokens = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "expires_at": "9999999999",
        }
        mock_supabase_writer.insert_record.return_value = True

        result = token_handler._store_and_return_tokens(tokens, "test_table")
        assert "access_token" in result
        assert "access_token_creation" in result

    def test_store_and_return_tokens_failure(self, token_handler, mock_supabase_writer):
        tokens = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "expires_at": "9999999999",
        }
        mock_supabase_writer.insert_record.return_value = False

        with pytest.raises(exceptions.TokenError):
            token_handler._store_and_return_tokens(tokens, "test_table")
