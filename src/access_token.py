import logging
from typing import Any

import supabase
from dotenv import load_dotenv

from src.infrastructure.auth.credentials import (
    FernetSecrets,
    StravaSecrets,
    SupabaseSecrets,
)
from src.infrastructure.auth.token_handler import TokenHandler
from src.infrastructure.auth.token_manager import TokenManager
from src.infrastructure.database.supabase_deleter import SupabaseDeleter
from src.infrastructure.database.supabase_reader import SupabaseReader
from src.infrastructure.database.supabase_writer import SupabaseWriter
from src.infrastructure.encryption.encryptor import FernetEncryptor

logger = logging.getLogger(__name__)


class GetAccessToken:
    def __init__(self) -> None:
        load_dotenv()

        self.credentials = self._load_credentials()
        self.supabase_client = self._create_supabase_client()
        self.supabase_reader = self._create_supabase_reader()
        self.supabase_writer = self._create_supabase_writer()
        self.supabase_deleter = self._create_supabase_deleter()
        self.token_manager = self._create_token_manager()
        self.encryptor = self._create_encryptor()
        self.token_handler = self._create_token_handler()

    def get_access_token(self) -> str | int:
        self.token_handler.process_token(
            self.credentials["supabase_secrets"].supabase_table,
        )
        access_token = self.supabase_reader.fetch_latest_record(
            self.credentials["supabase_secrets"].supabase_table,
            "access_token",
            "access_token",
        )
        if access_token is None:
            logger.error("No access token found in the database.")
            raise ValueError("No access token found in the database.")

        return self.encryptor.decrypt_value(
            data_to_decrypt=access_token, value="access_token"
        )

    def _load_credentials(self) -> dict[str, Any]:
        return {
            "supabase_secrets": SupabaseSecrets(),
            "strava_secrets": StravaSecrets(),
            "fernet_secrets": FernetSecrets(),
        }

    def _create_supabase_client(self) -> supabase.Client:
        supabase_secrets = self.credentials["supabase_secrets"]
        return supabase.create_client(
            supabase_secrets.supabase_url,
            supabase_secrets.supabase_api_key,
        )

    def _create_supabase_reader(self) -> SupabaseReader:
        return SupabaseReader(client=self.supabase_client)

    def _create_supabase_writer(self) -> SupabaseWriter:
        return SupabaseWriter(client=self.supabase_client)

    def _create_supabase_deleter(self) -> SupabaseDeleter:
        return SupabaseDeleter(client=self.supabase_client)

    def _create_token_manager(self) -> TokenManager:
        strava_secrets = self.credentials["strava_secrets"]
        return TokenManager(
            client_id=strava_secrets.strava_client_id,
            secret_key=strava_secrets.strava_secret_key,
        )

    def _create_encryptor(self) -> FernetEncryptor:
        fernet_secrets = self.credentials["fernet_secrets"]
        return FernetEncryptor(cipher=fernet_secrets.cipher)

    def _create_token_handler(self) -> TokenHandler:
        strava_secrets = self.credentials["strava_secrets"]
        return TokenHandler(
            supabase_reader=self.supabase_reader,
            supabase_writer=self.supabase_writer,
            supabase_deleter=self.supabase_deleter,
            token_manager=self.token_manager,
            encryptor=self.encryptor,
            client_id=strava_secrets.strava_client_id,
        )
