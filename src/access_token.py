from pathlib import Path

from dotenv import load_dotenv

from src.core.auth.service import AccessTokenService
from src.infrastructure.auth.credentials import (
    FernetSecrets,
    StravaSecrets,
    get_default_key_path,
    get_default_token_path,
)
from src.infrastructure.auth.oauth_code import GetOauthCode
from src.infrastructure.auth.strava_token_gateway import StravaTokenGateway
from src.infrastructure.persistence.encrypted_file_token_store import (
    EncryptedFileTokenStore,
)


class GetAccessToken:
    """Composition facade for obtaining a valid Strava access token."""

    def __init__(
        self,
        service: AccessTokenService | None = None,
        token_path: Path | None = None,
        key_path: Path | None = None,
    ) -> None:
        load_dotenv()
        self._service = (
            service
            if service is not None
            else self._build_service(token_path, key_path)
        )

    def get_access_token(self) -> str:
        return self._service.get_access_token()

    @staticmethod
    def _build_service(
        token_path: Path | None,
        key_path: Path | None,
    ) -> AccessTokenService:
        credentials = StravaSecrets()
        cipher = FernetSecrets(key_path or get_default_key_path()).cipher
        token_store = EncryptedFileTokenStore(
            path=token_path or get_default_token_path(),
            cipher=cipher,
        )
        token_gateway = StravaTokenGateway(
            client_id=credentials.strava_client_id,
            secret_key=credentials.strava_secret_key,
        )
        return AccessTokenService(
            token_store=token_store,
            token_gateway=token_gateway,
            authorization_code_provider=GetOauthCode(),
            client_id=credentials.strava_client_id,
        )
