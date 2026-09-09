import logging
from enum import StrEnum
from typing import cast

import requests

from src.domain.token import TokenSet
from src.utils import constants
from src.utils.exceptions import TokenError

logger = logging.getLogger(__name__)


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
                constants.URL_GET_ACCESS_TOKEN,
                data=data,
                timeout=self._request_timeout,
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise TypeError("Strava returned a non-object token payload.")
            return TokenSet.from_mapping(cast(dict[str, object], payload))
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
