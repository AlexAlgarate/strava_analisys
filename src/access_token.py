import supabase
from dotenv import load_dotenv

from src.credentials import FernetSecrets, StravaSecrets, SupabaseSecrets
from src.database import SupabaseReader, SupabaseWriter
from src.encryptor import FernetEncryptor
from src.token_handler import TokenHandler
from src.token_manager import TokenManager
from src.utils.logging import Logger


class GetAccessToken:
    def __init__(self, logger: Logger):
        load_dotenv()
        self.logger = logger

        self.credentials = self._load_credentials()
        self.supabase_reader = self._create_supabase_reader()
        self.supabase_writer = self._create_supabase_writer()
        self.token_manager = self._create_token_manager()
        self.encryptor = self._create_encryptor()
        self.token_handler = self._create_token_handler()

    def get_access_token(self) -> str:
        self.token_handler.process_token(
            self.credentials["supabase_secrets"].SUPABASE_TABLE
        )
        access_token = self.supabase_reader.fetch_latest_record(
            self.credentials["supabase_secrets"].SUPABASE_TABLE,
            "access_token",
            "access_token",
        )
        return self.encryptor.decrypt_value(
            data_to_decrypt=access_token, value="access_token"
        )

    def _load_credentials(self):
        return {
            "supabase_secrets": SupabaseSecrets(),
            "strava_secrets": StravaSecrets(),
            "fernet_secrets": FernetSecrets(),
        }

    def _create_supabase_reader(self) -> SupabaseReader:
        supabase_secrets = self.credentials["supabase_secrets"]
        return SupabaseReader(
            client=supabase.create_client(
                supabase_secrets.SUPABASE_URL,
                supabase_secrets.SUPABASE_API_KEY,
            )
        )

    def _create_supabase_writer(self) -> SupabaseWriter:
        supabase_secrets = self.credentials["supabase_secrets"]
        return SupabaseWriter(
            client=supabase.create_client(
                supabase_secrets.SUPABASE_URL,
                supabase_secrets.SUPABASE_API_KEY,
            )
        )

    def _create_token_manager(self) -> TokenManager:
        strava_secrets = self.credentials["strava_secrets"]
        return TokenManager(
            client_id=strava_secrets.STRAVA_CLIENT_ID,
            secret_key=strava_secrets.STRAVA_SECRET_KEY,
            logger=self.logger,
        )

    def _create_encryptor(self) -> FernetEncryptor:
        fernet_secrets = self.credentials["fernet_secrets"]
        return FernetEncryptor(cipher=fernet_secrets.CIPHER, logger=self.logger)

    def _create_token_handler(self) -> TokenHandler:
        strava_secrets = self.credentials["strava_secrets"]
        return TokenHandler(
            supabase_reader=self.supabase_reader,
            supabase_writer=self.supabase_writer,
            token_manager=self.token_manager,
            encryptor=self.encryptor,
            client_id=strava_secrets.STRAVA_CLIENT_ID,
            logger=self.logger,
        )
