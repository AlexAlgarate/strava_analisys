from src.interfaces.strava_api import HTTPClient
from src.requests_services import AioHTTPClient

from .base_strava_api import BaseStravaAPI


class AsyncStravaAPI(BaseStravaAPI):
    def __init__(self, access_token: str, http_client: HTTPClient = None):
        super().__init__(access_token)
        self.http_client = http_client or AioHTTPClient()

    async def make_request_async(self, endpoint: str, params: dict = None) -> dict:
        url = self._get_url(endpoint)
        return await self.http_client.get(
            url, headers=self._get_headers(), params=params
        )
