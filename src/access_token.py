from dotenv import load_dotenv

from src.credentials import FernetSecrets, StravaSecrets, SupabaseSecrets
from src.database import SupabaseClient
from src.encryptor import DataEncryptor
from src.token_handler import TokenHandler
from src.token_manager import TokenManager


class GetAccessToken:
    def __init__(self):
        load_dotenv()
        self.credentials = self._load_credentials()
        self.supabase_client = self._create_supabase_client()
        self.token_manager = self._create_token_manager()
        self.encryptor = self._create_encryptor()
        self.token_handler = self._create_token_handler()

    def get_access_token(self):
        self.token_handler.process_token(
            self.credentials["supabase_secrets"].SUPABASE_TABLE
        )
        access_token = self.supabase_client.fetch_latest_record(
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

    def _create_supabase_client(self) -> SupabaseClient:
        supabase_secrets = self.credentials["supabase_secrets"]
        return SupabaseClient(
            supabase_secrets.SUPABASE_URL, supabase_secrets.SUPABASE_API_KEY
        )

    def _create_token_manager(self) -> TokenManager:
        strava_secrets = self.credentials["strava_secrets"]
        return TokenManager(
            client_id=strava_secrets.STRAVA_CLIENT_ID,
            secret_key=strava_secrets.STRAVA_SECRET_KEY,
        )

    def _create_encryptor(self) -> DataEncryptor:
        fernet_secrets = self.credentials["fernet_secrets"]
        return DataEncryptor(fernet_secrets.CIPHER)

    def _create_token_handler(self) -> TokenHandler:
        strava_secrets = self.credentials["strava_secrets"]
        return TokenHandler(
            supabase_client=self.supabase_client,
            token_manager=self.token_manager,
            encryptor=self.encryptor,
            client_id=strava_secrets.STRAVA_CLIENT_ID,
        )
