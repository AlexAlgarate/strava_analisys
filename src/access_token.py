from abc import ABC, abstractmethod
from typing import Dict, Optional, Union

from dotenv import load_dotenv

from src.credentials import FernetSecrets, StravaSecrets, SupabaseSecrets
from src.database import SupabaseClient
from src.encryptor import DataEncryptor
from src.token_handler import TokenHandler
from src.token_manager import TokenManager


class IEncryptor(ABC):
    @abstractmethod
    def decrypt_value(self, value: str) -> str:
        pass

    @abstractmethod
    def encrypt_data(self, data: Dict[str, Union[str, int]]) -> Dict[str, str]:
        pass

    @abstractmethod
    def decrypt_data(
        self, data: Dict[str, Union[str, int]]
    ) -> Dict[str, Union[str, int]]:
        pass


class ITokenManager(ABC):
    @abstractmethod
    def refresh_access_token(
        self, refresh_token: str
    ) -> Optional[Dict[str, Union[str, int]]]:
        pass

    @abstractmethod
    def get_initial_tokens(self, code: str) -> Optional[Dict[str, Union[str, int]]]:
        pass


class IDatabaseClient(ABC):
    @abstractmethod
    def fetch_latest_record(
        self, table: str, column: str, order_by: Optional[str] = None
    ) -> Optional[Dict[str, Union[str, int]]]:
        pass

    @abstractmethod
    def insert_record(self, table: str, data: Dict[str, Union[str, int]]) -> bool:
        pass


class ITokenHandler(ABC):
    @abstractmethod
    def process_token(self, table: str):
        pass


class TokenService(ABC):
    def __init__(
        self,
        database_client: IDatabaseClient,
        token_manager: ITokenManager,
        encryptor: IEncryptor,
    ):
        self.database_client = database_client
        self.token_manager = token_manager
        self.encryptor = encryptor

    def get_access_token(self, table: str) -> str:
        last_access_token = self.database_client.fetch_latest_record(
            table, "access_token", "access_token"
        )
        return self.encryptor.decrypt_value(last_access_token)


class SupabaseClientAdapter(IDatabaseClient):
    def __init__(self, credentials: SupabaseSecrets):
        self.client = SupabaseClient(
            credentials.SUPABASE_URL, credentials.SUPABASE_API_KEY
        )

    def fetch_latest_record(self, table: str, column: str, key: str) -> str:
        return self.client.fetch_latest_record(table, column, key)


class StravaTokenManagerAdapter(ITokenManager):
    def __init__(self, credentials: StravaSecrets):
        self.manager = TokenManager(
            credentials.STRAVA_CLIENT_ID, credentials.STRAVA_SECRET_KEY
        )

    def process_token(self, credentials: dict) -> str:
        return self.manager.process_token(credentials)


class FernetEncryptorAdapter(IEncryptor):
    def __init__(self, cipher: str):
        self.encryptor = DataEncryptor(cipher)

    def decrypt_value(self, value: str) -> str:
        return self.encryptor.decrypt_value(value)


def get_access_token_abc() -> str:
    load_dotenv()

    supabase_credentials = SupabaseSecrets
    strava_credentials = StravaSecrets
    fernet_credentials = FernetSecrets

    database_client = SupabaseClientAdapter(supabase_credentials)
    token_manager = StravaTokenManagerAdapter(strava_credentials)
    encryptor = FernetEncryptorAdapter(fernet_credentials.CIPHER)

    token_service = TokenService(database_client, token_manager, encryptor)

    token_service.token_manager.process_token(supabase_credentials.SUPABASE_TABLE)
    return token_service.get_access_token(supabase_credentials.SUPABASE_TABLE)


# class TokenService:
#     def __init__(
#         self,
#         database_client: IDatabaseClient,
#         token_manager: ITokenManager,
#         encryptor: IEncryptor,
#     ):
#         self.database_client = database_client
#         self.token_manager = token_manager
#         self.encryptor = encryptor

#     def get_access_token(self, table: str) -> str:
#         last_access_token = self.database_client.fetch_latest_record(
#             table, "access_token", "access_token"
#         )
#         return self.encryptor.decrypt_value(last_access_token)


# class SupabaseClientAdapter(IDatabaseClient):
#     def __init__(self, credentials: SupabaseSecrets):
#         self.client = SupabaseClient(
#             credentials.SUPABASE_URL, credentials.SUPABASE_API_KEY
#         )

#     def fetch_latest_record(self, table: str, column: str, key: str) -> str:
#         return self.client.fetch_latest_record(table, column, key)


# class StravaTokenManagerAdapter(ITokenManager):
#     def __init__(self, credentials: StravaSecrets):
#         self.manager = TokenManager(
#             credentials.STRAVA_CLIENT_ID, credentials.STRAVA_SECRET_KEY
#         )

#     def process_token(self, credentials: dict) -> str:
#         return self.manager.process_token(credentials)


# class FernetEncryptorAdapter(IEncryptor):
#     def __init__(self, cipher: str):
#         self.encryptor = DataEncryptor(cipher)

#     def decrypt_value(self, value: str) -> str:
#         return self.encryptor.decrypt_value(value)


# # Main function to get access token
# def get_access_token() -> str:
#     load_dotenv()

#     supabase_credentials = SupabaseSecrets
#     strava_credentials = StravaSecrets
#     fernet_credentials = FernetSecrets

#     # Create instances using adapters
#     database_client = SupabaseClientAdapter(supabase_credentials)
#     token_manager = StravaTokenManagerAdapter(strava_credentials)
#     encryptor = FernetEncryptorAdapter(fernet_credentials.CIPHER)

#     # Inject dependencies into the TokenService
#     token_service = TokenService(database_client, token_manager, encryptor)

#     # Process token and get the access token
#     token_service.token_manager.process_token(supabase_credentials.SUPABASE_TABLE)
#     return token_service.get_access_token(supabase_credentials.SUPABASE_TABLE)


def get_access_token() -> str:
    load_dotenv()

    supabase_credentials = SupabaseSecrets()
    strava_credentials = StravaSecrets()
    fernet_credentials = FernetSecrets()

    database_client = SupabaseClient(
        supabase_credentials.SUPABASE_URL, supabase_credentials.SUPABASE_API_KEY
    )
    token_manager = TokenManager(
        client_id=strava_credentials.STRAVA_CLIENT_ID,
        secret_key=strava_credentials.STRAVA_SECRET_KEY,
    )
    encryptor = DataEncryptor(fernet_credentials.CIPHER)

    token_service = TokenHandler(
        supabase_client=database_client,
        token_manager=token_manager,
        encryptor=encryptor,
        client_id=strava_credentials.STRAVA_CLIENT_ID,
    )

    token_service.process_token(supabase_credentials.SUPABASE_TABLE)

    access_token = database_client.fetch_latest_record(
        supabase_credentials.SUPABASE_TABLE, "access_token", "access_token"
    )
    return encryptor.decrypt_value(data_to_decrypt=access_token, value="access_token")
