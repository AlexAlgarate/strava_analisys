from datetime import datetime
from typing import Dict, Optional, Union

from src import utils as utils
from src.credentials import StravaSecrets
from src.encryptor import DataEncryptor
from src.oauth_code import OAuthHelper
from src.supabase_db import SupabaseClient
from src.token_manager import TokenManager


class TokenHandler:
    """Coordina el flujo de manejo de tokens."""

    def __init__(
        self,
        supabase_client: SupabaseClient,
        token_manager: TokenManager,
        encryptor: DataEncryptor,
    ):
        self.supabase_client = supabase_client
        self.token_manager = token_manager
        self.encryptor = encryptor

    def process_token(self, table: str):
        record = self.supabase_client.fetch_latest_record(table, "*", "expires_at")

        if record:
            self._process_exisiting_token(record, table)
        else:
            print("No data found in Supabase. Generating initial tokens...\n")
            self._prepare_initial_token(table)

        return record

    def _process_exisiting_token(
        self, record: dict, table: str
    ) -> Optional[Dict[str, Union[int, str]]]:
        try:
            decrypted_record = self.encryptor.decrypt_data(record)

            if self.token_manager.token_has_expired(
                int(decrypted_record["expires_at"])
            ):
                print("Token expired, refreshing...")
                refresh_token = decrypted_record["refresh_token"]
                new_tokens = self.token_manager.refresh_access_token(refresh_token)

                if new_tokens:
                    return self._store_and_return_tokens(new_tokens, table)

        except Exception as e:
            print(f"Error processing token: {e}")
            return None

    def _prepare_initial_token(
        self, table: str
    ) -> Optional[Dict[str, Union[int, str]]]:
        try:
            oauth_helper = OAuthHelper()
            code = oauth_helper.get_authorization_code(
                utils.base_url_oauth,
                {
                    "client_id": StravaSecrets.STRAVA_CLIENT_ID,
                    "response_type": "code",
                    "redirect_uri": "http://localhost/exchange_token",
                    "approval_prompt": "force",
                    "scope": "read,read_all,activity:read,activity:read_all",
                },
            )
            initial_tokens = self.token_manager.get_initial_tokens(code)

            if initial_tokens:
                return self._store_and_return_tokens(initial_tokens, table)

        except Exception as e:
            print(f"Error processing initial tokens: {e}")
        return None

    def _store_and_return_tokens(
        self,
        tokens: dict,
        table: str,
    ) -> Dict[str, Union[str, int]]:
        try:
            data_to_insert = self._prepare_data_for_insertion(tokens)
            encrypted_data = self.encryptor.encrypt_data(data_to_insert)

            if self.supabase_client.insert_record(table, encrypted_data):
                return data_to_insert

        except Exception as e:
            print(f"Error storing tokens: {e}")
            return {}

    @staticmethod
    def _prepare_data_for_insertion(
        tokens: Dict[str, Union[str, datetime]],
    ) -> Dict[str, Union[str, datetime]]:
        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "expires_at": tokens["expires_at"],
            "access_token_creation": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
