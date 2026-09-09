import logging
from enum import StrEnum

import requests

from src.domain.token import TokenSet
from src.infrastructure.serialization.token import token_from_mapping
from src.utils.exceptions import TokenError

logger = logging.getLogger(__name__)
TOKEN_URL = "https://www.strava.com/oauth/token"


class GrantType(StrEnum):
    REFRESH_TOKEN = "refresh_token"
    AUTHORIZATION_CODE = "authorization_code"


class StravaTokenGateway:
    """Exchange OAuth grants for tokens using Strava's HTTP endpoint."""

    def __init__(
        self,
        client_id: str,
        secret_key: str,
        request_timeout: float = 10.0,
    ) -> None:
        self.client_id = client_id
        self.secret_key = secret_key
        self._request_timeout = request_timeout

    def _prepare_request_data(
        self, grant_type: GrantType, **kwargs: str
    ) -> dict[str, str]:
        return {
            "client_id": self.client_id,
            "client_secret": self.secret_key,
            "grant_type": grant_type.value,
            **kwargs,
        }

    def _send_token_request(self, data: dict[str, str]) -> TokenSet:
        try:
            response = requests.post(
                TOKEN_URL,
                data=data,
                timeout=self._request_timeout,
            )
            response.raise_for_status()
            return token_from_mapping(response.json())
        except (requests.RequestException, TypeError, ValueError) as exc:
            logger.exception("Strava token request failed")
            raise TokenError("Could not obtain OAuth tokens from Strava.") from exc

    def refresh_access_token(self, refresh_token: str) -> TokenSet:
        data = self._prepare_request_data(
            grant_type=GrantType.REFRESH_TOKEN,
            refresh_token=refresh_token,
        )
        return self._send_token_request(data)

    def exchange_authorization_code(self, code: str) -> TokenSet:
        data = self._prepare_request_data(
            grant_type=GrantType.AUTHORIZATION_CODE,
            code=code,
        )
        return self._send_token_request(data)
