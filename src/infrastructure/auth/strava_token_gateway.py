import logging
from enum import StrEnum
from math import isfinite

import requests

from src.application.errors import TokenError
from src.domain.token import TokenSet
from src.infrastructure.serialization.token import token_from_mapping

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
        self._client_id = _require_non_empty_text("Strava client ID", client_id)
        self._secret_key = _require_non_empty_text(
            "Strava client secret",
            secret_key,
        )
        if isinstance(request_timeout, bool) or not isinstance(
            request_timeout,
            (int, float),
        ):
            raise TypeError("OAuth request timeout must be numeric.")
        if not isfinite(request_timeout) or request_timeout <= 0:
            raise ValueError("OAuth request timeout must be a finite positive number.")
        self._request_timeout = float(request_timeout)

    def _prepare_request_data(
        self, grant_type: GrantType, **kwargs: str
    ) -> dict[str, str]:
        return {
            "client_id": self._client_id,
            "client_secret": self._secret_key,
            "grant_type": grant_type.value,
            **kwargs,
        }

    def _send_token_request(self, data: dict[str, str]) -> TokenSet:
        try:
            response = requests.post(
                TOKEN_URL,
                data=data,
                timeout=self._request_timeout,
                allow_redirects=False,
            )
            response.raise_for_status()
            if not 200 <= response.status_code < 300:
                raise requests.HTTPError(
                    "Strava OAuth endpoint returned a non-success status.",
                    response=response,
                )
            return token_from_mapping(response.json())
        except (requests.RequestException, TypeError, ValueError) as exc:
            logger.exception("Strava token request failed")
            raise TokenError("Could not obtain OAuth tokens from Strava.") from exc

    def refresh_access_token(self, refresh_token: str) -> TokenSet:
        validated_refresh_token = _require_non_empty_text(
            "Refresh token",
            refresh_token,
        )
        data = self._prepare_request_data(
            grant_type=GrantType.REFRESH_TOKEN,
            refresh_token=validated_refresh_token,
        )
        return self._send_token_request(data)

    def exchange_authorization_code(self, code: str) -> TokenSet:
        validated_code = _require_non_empty_text("Authorization code", code)
        data = self._prepare_request_data(
            grant_type=GrantType.AUTHORIZATION_CODE,
            code=validated_code,
        )
        return self._send_token_request(data)


def _require_non_empty_text(name: str, value: object) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string.")
    if not value.strip():
        raise ValueError(f"{name} cannot be empty.")
    return value
