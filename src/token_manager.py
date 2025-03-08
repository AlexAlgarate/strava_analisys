import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Union

import requests

from src.utils import constants as constant
from src.utils import helpers as helper

TokenResponse = Dict[str, Union[str, int]]
RequestData = Dict[str, str]


class GranType(Enum):
    REFRESH_TOKEN = "refresh_token"
    AUTHORIZATION_CODE = "authorization_code"


@dataclass
class Credentials:
    client_id: str
    secret_key: str


class TokenException(Exception):
    """Custom exception for token-related errors."""

    pass


class TokenManager:
    """Manages token-related operations."""

    def __init__(self, client_id: str, secret_key: str, logger: helper.Logger):
        """
        Initializes the TokenManager with the necessary credentials.

        Args:
            client_id (str): The client ID.
            secret_key (str): The client secret key.
        """

        self.credentials = Credentials(client_id, secret_key)
        self.logger = logger

    @staticmethod
    def token_has_expired(expires_at: int) -> bool:
        """
        Checks if a token has expired.

        Args:
            expires_at (int): The expiration timestamp of the token.

        Returns:
            bool: True if token has expired, False otherwise.
        """

        return int(expires_at) < int(time.time())

    def _prepare_request_data(self, gran_type: GranType, **kwargs) -> RequestData:
        """
        Prepare the request data for token operations.

        Args:
            grant_type (GranType): Type of grant request
            **kwargs: Additional parameters for the request

        Returns:
            Dict of requests parameters
        """

        data = {
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.secret_key,
            "grant_type": gran_type.value,
        }
        data.update(kwargs)
        return data

    def _send_token_request(self, data: Dict[str, str]) -> Optional[TokenResponse]:
        """
        Sends a token request to the API.

        Args:
            data (Dict[str, str]): The data to send in the request.

        Returns:
            Optional[TokenResponse]: The JSON response from the API, or None in case of an error.
        """

        try:
            response = requests.post(constant.URL_GET_ACCESS_TOKEN, data=data)
            response.raise_for_status()
            return response.json()

        except TokenException as e:
            self.logger.error(f"Error fetching initial tokens: {e}", exc_info=True)
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[TokenResponse]:
        """
        Refreshes the access token using a refresh token.

        Args:
            refresh_token (str): The refresh token.

        Returns:
            Optional[TokenResponse]: The new access token, or None if an error occurs.
        """

        data = self._prepare_request_data(
            gran_type=GranType.REFRESH_TOKEN,
            refresh_token=refresh_token,
        )

        return self._send_token_request(data)

    def get_initial_tokens(self, code: str) -> Optional[TokenResponse]:
        """
        Get initial access and refresh token.

        Args:
            code (str): The authorization code from OAuth.

        Returns:
            Initial tokens if successfull, None otherwise..
        """

        data = self._prepare_request_data(
            gran_type=GranType.AUTHORIZATION_CODE,
            code=code,
        )
        return self._send_token_request(data)
