from collections.abc import Mapping
from dataclasses import dataclass
from types import TracebackType
from typing import Self

from src.infrastructure.api_clients.protocols import AsyncHttpClient

from .async_http_client import AsyncHTTPClient


@dataclass(frozen=True, slots=True)
class StravaAPIConfig:
    base_url: str = "https://www.strava.com/api/v3"
    content_type: str = "application/json"


class AsyncStravaAPI:
    def __init__(
        self,
        access_token: str,
        config: StravaAPIConfig | None = None,
        http_client: AsyncHttpClient | None = None,
    ) -> None:
        if not access_token:
            raise ValueError("Access token must be provided.")
        self._access_token = access_token
        self._owns_http_client = http_client is None
        self._http_client = http_client or AsyncHTTPClient()
        self._config = config or StravaAPIConfig()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        if self._owns_http_client:
            await self._http_client.close()

    def get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": self._config.content_type,
        }

    def get_url(self, endpoint: str) -> str:
        return f"{self._config.base_url}{endpoint}"

    async def make_request(
        self,
        endpoint: str,
        params: Mapping[str, str | int] | None = None,
    ) -> object:
        url = self.get_url(endpoint)
        headers = self.get_headers()
        return await self._http_client.make_async_request(
            url=url,
            headers=headers,
            params=params,
        )
