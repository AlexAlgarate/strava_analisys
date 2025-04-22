from ..http.http_clients import SyncHTTPClient
from .base_strava_api import BaseStravaAPI, StravaAPIConfig


class SyncStravaAPI(BaseStravaAPI):
    def __init__(self, access_token: str, config: StravaAPIConfig = None):
        super().__init__(
            access_token=access_token, http_client=SyncHTTPClient(), config=config
        )

    def make_request(self, endpoint: str, params: dict = None) -> dict:
        url = self.get_url(endpoint)
        return self.http_client.get(url, headers=self.get_headers(), params=params)
