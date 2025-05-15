import logging
import time
from enum import Enum
from typing import Any, Dict, cast

import requests

from src.utils import constants as constant
from src.utils import exceptions

logger = logging.getLogger(__name__)


class GranType(Enum):
    REFRESH_TOKEN = "refresh_token"
    AUTHORIZATION_CODE = "authorization_code"


class TokenManager:
    def __init__(self, client_id: str, secret_key: str):
        self.client_id = client_id
        self.secret_key = secret_key

    @staticmethod
    def token_has_expired(expires_at: int) -> bool:
        return int(expires_at) < int(time.time())

    def _prepare_request_data(
        self, gran_type: GranType, **kwargs: str
    ) -> Dict[str, str]:
        data = {
            "client_id": self.client_id,
            "client_secret": self.secret_key,
            "grant_type": gran_type.value,
        }
        data.update(kwargs)
        return data

    def _send_token_request(
        self, data: Dict[str, str]
    ) -> Dict[str, Any] | None:
        try:
            response = requests.post(constant.URL_GET_ACCESS_TOKEN, data=data)
            response.raise_for_status()
            response_json = response.json()
            return cast(Dict[str, Any], response_json)

        except exceptions.TokenException as e:
            logger.error(f"Error fetching initial tokens: {e}", exc_info=True)
            return None

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any] | None:
        data = self._prepare_request_data(
            gran_type=GranType.REFRESH_TOKEN,
            refresh_token=refresh_token,
        )

        return self._send_token_request(data)

    def get_initial_tokens(self, code: str) -> Dict[str, Any] | None:
        data = self._prepare_request_data(
            gran_type=GranType.AUTHORIZATION_CODE,
            code=code,
        )
        return self._send_token_request(data)
