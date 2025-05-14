import logging
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional

from src.infrastructure.auth.oauth_code import GetOauthCode
from src.infrastructure.auth.token_manager import TokenManager
from src.infrastructure.database.supabase_deleter import SupabaseDeleter
from src.infrastructure.database.supabase_reader import SupabaseReader
from src.infrastructure.database.supabase_writer import SupabaseWriter
from src.interfaces.encryption.encryptor import IEncryptation
from src.utils import constants as constant
from src.utils import exceptions as exception

logger = logging.getLogger(__name__)


def handle_token_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise exception.TokenError(f"Token operation failed: {str(e)}") from e

    return wrapper


@dataclass
class Credentials:
    client_id: str


class TokenHandler:
    def __init__(
        self,
        supabase_reader: SupabaseReader,
        supabase_writer: SupabaseWriter,
        supabase_deleter: SupabaseDeleter,
        token_manager: TokenManager,
        encryptor: IEncryptation,
        client_id: str,
        logger: Optional[logging.Logger] = None,
    ):
        self.supabase_reader = supabase_reader
        self.supabase_writer = supabase_writer
        self.supabase_deleter = supabase_deleter
        self.token_manager = token_manager
        self.encryptor = encryptor
        self.credentials = Credentials(client_id)

    def process_token(self, table: str) -> Any:
        record = self.supabase_reader.fetch_latest_record(table, "*", "expires_at")

        if not record:
            logger.info("No data found in Supabase. Generating initial tokens...\n")
            self._handle_initial_token_flow(table)
            return {}
        return self._handle_exisiting_token(record, table)

    @handle_token_errors
    def _cleanup_expired_tokens(self, table: str) -> None:
        try:
            if self.supabase_deleter.cleanup_expired_tokens(table, self.encryptor):
                logger.info("Successfully cleaned up expired tokens")
        except exception.DatabaseOperationError as e:
            logger.warning(f"Failed to cleanup expired tokens: {e}")

    @handle_token_errors
    def _handle_exisiting_token(self, record: Dict[str, int | str], table: str) -> Any:
        decrypted_record = self.encryptor.decrypt_data(record)

        if self.token_manager.token_has_expired(int(decrypted_record["expires_at"])):
            logger.info("Token expired, refreshing...")
            return self._refresh_and_store_token(
                decrypted_record["refresh_token"], table
            )

        return decrypted_record

    @handle_token_errors
    def _handle_initial_token_flow(self, table: str) -> Any:
        oauth_helper = GetOauthCode()
        code = oauth_helper.get_authorization_code(
            constant.OAUTH_URL,
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

        return None

    @handle_token_errors
    def _refresh_and_store_token(self, refresh_token: str, table: str) -> Any:
        new_tokens = self.token_manager.refresh_access_token(refresh_token)

        if not new_tokens:
            raise exception.TokenError("Token refresh failed.")

        return self._store_and_return_tokens(new_tokens, table)

    @handle_token_errors
    def _store_and_return_tokens(
        self, tokens: Dict[str, str | int], table: str
    ) -> Dict[str, int | str]:
        data_to_insert = self._prepare_token_data(tokens)
        encrypted_data = self.encryptor.encrypt_data(data=data_to_insert)

        if not self.supabase_writer.insert_record(table, encrypted_data):
            raise exception.TokenError("Failed to store tokens in database")

        return data_to_insert

    @staticmethod
    def _prepare_token_data(tokens: Dict[str, str | int]) -> Dict[str, str | int]:
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_at": tokens["expires_at"],
            "access_token_creation": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
