from src.interfaces.strava_api import IHTTPClient
from src.strava_api.requests_services import AioHTTPClient

from .base_strava_api import BaseStravaAPI


class AsyncStravaAPI(BaseStravaAPI):
    def __init__(self, access_token: str, http_client: IHTTPClient = None):
        super().__init__(access_token)
        self.http_client = http_client or AioHTTPClient()

    async def make_request_async(self, endpoint: str, params: dict = None) -> dict:
        url = self.get_url(endpoint)
        return await self.http_client.get(
            url, headers=self.get_headers(), params=params
        )
