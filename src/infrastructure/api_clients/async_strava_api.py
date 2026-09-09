from typing import Any, cast

from src.interfaces.api_clients.async_http_client import BaseASyncHTTPClient
from src.interfaces.api_clients.strava_api import BaseStravaAPI, StravaAPIConfig

from .async_http_client import AsyncHTTPClient


class AsyncStravaAPI(BaseStravaAPI):
    def __init__(
        self,
        access_token: str,
        config: StravaAPIConfig | None = None,
        http_client: BaseASyncHTTPClient | None = None,
    ) -> None:
        super().__init__(
            access_token=access_token,
            http_client=http_client or AsyncHTTPClient(),
            config=config,
        )

    async def make_request(
        self, endpoint: str, params: dict | None = None
    ) -> dict[str, Any]:
        url = self.get_url(endpoint)
        headers = self.get_headers()
        client = cast(BaseASyncHTTPClient, self.http_client)

        return await client.make_async_request(
            url=url,
            headers=headers,
            params=params,
        )
