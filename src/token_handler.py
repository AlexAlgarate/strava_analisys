from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from typing import Dict, Optional, Union

from src import utils as utils
from src.database import SupabaseClient
from src.encryptor import DataEncryptor
from src.oauth_code import GetOauthCode
from src.token_manager import TokenManager

TokenResponse = Dict[str, Union[int, str]]


class TokenError(Exception):
    """Custom exception for token-related operations."""

    pass


def handle_token_errors(func):
    """Decorator for consistent error handling in token operations."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise TokenError(f"Token operation failed: {str(e)}") from e

    return wrapper


@dataclass
class Credentials:
    client_id: str


class TokenHandler:
    def __init__(
        self,
        supabase_client: SupabaseClient,
        token_manager: TokenManager,
        encryptor: DataEncryptor,
        client_id: str,
    ):
        self.supabase_client = supabase_client
        self.token_manager = token_manager
        self.encryptor = encryptor
        self.logger = utils.Logger().setup_logger()
        self.credentials = Credentials(client_id)

    def process_token(self, table: str):
        record = self.supabase_client.fetch_latest_record(table, "*", "expires_at")

        if not record:
            self.logger.info(
                "No data found in Supabase. Generating initial tokens...\n"
            )
            self._handle_initial_token_flow(table)

        return self._handle_exisiting_token(record, table)

    @handle_token_errors
    def _handle_exisiting_token(
        self, record: dict, table: str
    ) -> Optional[TokenResponse]:
        decrypted_record = self.encryptor.decrypt_data(record)

        if self.token_manager.token_has_expired(int(decrypted_record["expires_at"])):
            self.logger.info("Token expired, refreshing...")
            return self._refresh_and_store_token(
                decrypted_record["refresh_token"], table
            )

        return decrypted_record

    @handle_token_errors
    def _handle_initial_token_flow(self, table: str) -> Optional[TokenResponse]:
        oauth_helper = GetOauthCode()
        code = oauth_helper.get_authorization_code(
            utils.base_url_oauth,
            {
                "client_id": self.credentials.client_id,
                "response_type": "code",
                "redirect_uri": "http://localhost/exchange_token",
                "approval_prompt": "force",
                "scope": "read,read_all,activity:read,activity:read_all",
            },
        )
        initial_tokens = self.token_manager.get_initial_tokens(code)

        if initial_tokens:
            return self._store_and_return_tokens(initial_tokens, table)

    @handle_token_errors
    def _refresh_and_store_token(
        self, refresh_token: str, table: str
    ) -> Optional[TokenResponse]:
        new_tokens = self.token_manager.refresh_access_token(refresh_token)

        if not new_tokens:
            raise TokenError("Token refresh failed.")

        return self._store_and_return_tokens(new_tokens, table)

    @handle_token_errors
    def _store_and_return_tokens(self, tokens: dict, table: str) -> TokenResponse:
        data_to_insert = self._prepare_token_data(tokens)
        encrypted_data = self.encryptor.encrypt_data(data_to_insert)

        if not self.supabase_client.insert_record(table, encrypted_data):
            raise TokenError("Failed to store tokens in database")

        return data_to_insert

    @staticmethod
    def _prepare_token_data(tokens: Dict[str, str]) -> Dict[str, str]:
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_at": tokens["expires_at"],
            "access_token_creation": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
