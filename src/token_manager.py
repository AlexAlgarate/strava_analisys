import logging
import time
from typing import Dict, Optional, Union

import requests
from requests.exceptions import RequestException

from src import utils as utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TokenManager:
    """Manages token-related operations."""

    def __init__(self, client_id: str, secret_key: str):
        """
        Initializes the TokenManager with the necessary credentials.

        Args:
            client_id (str): The client ID.
            secret_key (str): The client secret key.
        """
        self.client_id = client_id
        self.secret_key = secret_key

    @staticmethod
    def token_has_expired(expires_at: int) -> bool:
        """
        Checks if the token has expired.

        Args:
            expires_at (int): The expiration timestamp of the token.

        Returns:
            bool: True if the token has expired, False otherwise.
        """
        return int(expires_at) < int(time.time())

    def _send_token_request(
        self, data: Dict[str, str]
    ) -> Optional[Dict[str, Union[str, int]]]:
        """
        Sends a token request to the API.

        Args:
            data (Dict[str, str]): The data to send in the request.

        Returns:
            Optional[Dict[str, Union[str, int]]]: The JSON response from the API, or None in case of an error.
        """
        try:
            response = requests.post(utils.base_url_access_token, data=data)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            logger.error(f"Error fetching initial tokens: {e}", exc_info=True)
            return None

    def refresh_access_token(
        self, refresh_token: str
    ) -> Optional[Dict[str, Union[str, int]]]:
        """
        Refreshes the access token using a refresh token.

        Args:
            refresh_token (str): The refresh token.

        Returns:
            Optional[Dict[str, Union[str, int]]]: The new access token, or None if an error occurs.
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.secret_key,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        return self._send_token_request(data)

    def get_initial_tokens(self, code: str) -> Optional[Dict[str, Union[str, int]]]:
        """
        Obtains the initial tokens using an authorization code.

        Args:
            code (str): The authorization code.

        Returns:
            Optional[Dict[str, Union[str, int]]]: The initial tokens, or None if an error occurs.
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.secret_key,
            "code": code,
            "grant_type": "authorization_code",
        }
        return self._send_token_request(data)
