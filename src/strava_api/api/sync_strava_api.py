from typing import Dict

from src.interfaces.strava_api import BaseStravaAPI

from ..http.http_clients import SyncHTTPClient
from .base_strava_api import StravaAPIConfig


class SyncStravaAPI(BaseStravaAPI):
    def __init__(self, access_token: str, config: StravaAPIConfig = None):
        super().__init__(
            access_token=access_token, http_client=SyncHTTPClient(), config=config
        )

    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": self.config.content_type,
        }

    def make_request(self, endpoint: str, params: dict = None) -> dict:
        url = self.get_url(endpoint)
        headers = self.get_headers()

        return self.http_client.get(url, headers=headers, params=params)
