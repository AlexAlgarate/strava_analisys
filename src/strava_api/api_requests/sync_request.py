from src.interfaces.strava_api import IHTTPClient
from src.strava_api.requests_services import RequestHTTPClient

from .base_strava_api import BaseStravaAPI


class SyncStravaAPI(BaseStravaAPI):
    def __init__(self, access_token: str, http_client: IHTTPClient = None):
        super().__init__(access_token)
        self.http_client = http_client or RequestHTTPClient()

    def make_request(self, endpoint: str, params: dict = None) -> dict:
        url = self.get_url(endpoint)
        return self.http_client.get(url, headers=self.get_headers(), params=params)
