from typing import Dict

from src.interfaces.strava_api import HTTPClient
from src.requests_services import AioHTTPClient, RequestHTTPClient


class BaseStravaAPI:
    BASE_URL = "https://www.strava.com/api/v3"

    def __init__(self, access_token: str):
        if not access_token:
            raise ValueError("\n\nAccess token must be provided.")
        self.access_token = access_token

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _get_url(self, endpoint: str) -> str:
        return f"{self.BASE_URL}{endpoint}"


class SyncStravaAPI(BaseStravaAPI):
    def __init__(self, access_token: str, http_client: HTTPClient = None):
        super().__init__(access_token)
        self.http_client = http_client or RequestHTTPClient()

    def make_request(self, endpoint: str, params: dict = None) -> dict:
        url = self._get_url(endpoint)
        return self.http_client.get(url, headers=self._get_headers(), params=params)


class AsyncStravaAPI(BaseStravaAPI):
    def __init__(self, access_token: str, http_client: HTTPClient = None):
        super().__init__(access_token)
        self.http_client = http_client or AioHTTPClient()

    async def make_request_async(self, endpoint: str, params: dict = None) -> dict:
        url = self._get_url(endpoint)
        return await self.http_client.get(
            url, headers=self._get_headers(), params=params
        )
