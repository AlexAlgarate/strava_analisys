from src.interfaces.strava_api import BaseStravaAPI, StravaAPIConfig

from ..http.http_clients import SyncHTTPClient


class SyncStravaAPI(BaseStravaAPI):
    def __init__(self, access_token: str, config: StravaAPIConfig = None):
        super().__init__(
            access_token=access_token,
            http_client=SyncHTTPClient(),
            config=config,
        )

    def make_request(self, endpoint: str, params: dict = None) -> dict:
        url = self.get_url(endpoint)
        headers = self.get_headers()

        return self.http_client.get_method(url, headers=headers, params=params)
