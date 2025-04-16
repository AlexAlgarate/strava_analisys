"""Asynchronous Strava API implementation."""

from ..http.http_clients import AsyncHTTPClient
from .base_strava_api import BaseStravaAPI, StravaAPIConfig


class AsyncStravaAPI(BaseStravaAPI):
    """Asynchronous implementation of Strava API."""

    def __init__(self, access_token: str, config: StravaAPIConfig = None):
        super().__init__(
            access_token=access_token, http_client=AsyncHTTPClient(), config=config
        )

    async def make_request_async(self, endpoint: str, params: dict = None) -> dict:
        """Make an asynchronous request to Strava API."""
        url = self.get_url(endpoint)
        return await self.http_client.get(
            url, headers=self.get_headers(), params=params
        )
