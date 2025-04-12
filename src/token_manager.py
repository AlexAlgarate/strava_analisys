import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict

import requests

from src.utils import constants as constant
from src.utils.logging import Logger

TokenResponse = Dict[str, str | int]
RequestData = Dict[str, str]


class GranType(Enum):
    REFRESH_TOKEN = "refresh_token"
    AUTHORIZATION_CODE = "authorization_code"


@dataclass
class Credentials:
    client_id: str
    secret_key: str


class TokenException(Exception):
    pass


class TokenManager:
    def __init__(self, client_id: str, secret_key: str, logger: Logger):
        self.credentials = Credentials(client_id, secret_key)
        self.logger = logger

    @staticmethod
    def token_has_expired(expires_at: int) -> bool:
        return int(expires_at) < int(time.time())

    def _prepare_request_data(self, gran_type: GranType, **kwargs) -> RequestData:
        data = {
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.secret_key,
            "grant_type": gran_type.value,
        }
        data.update(kwargs)
        return data

    def _send_token_request(self, data: Dict[str, str]) -> TokenResponse | None:
        try:
            response = requests.post(constant.URL_GET_ACCESS_TOKEN, data=data)
            response.raise_for_status()
            return response.json()

        except TokenException as e:
            self.logger.error(f"Error fetching initial tokens: {e}", exc_info=True)
            return None

    def refresh_access_token(self, refresh_token: str) -> TokenResponse | None:
        data = self._prepare_request_data(
            gran_type=GranType.REFRESH_TOKEN,
            refresh_token=refresh_token,
        )

        return self._send_token_request(data)

    def get_initial_tokens(self, code: str) -> TokenResponse | None:
        data = self._prepare_request_data(
            gran_type=GranType.AUTHORIZATION_CODE,
            code=code,
        )
        return self._send_token_request(data)
