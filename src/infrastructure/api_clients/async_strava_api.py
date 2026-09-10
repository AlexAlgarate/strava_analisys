from collections.abc import Mapping
from dataclasses import dataclass
from types import TracebackType
from typing import Self
from urllib.parse import urlsplit

from src.infrastructure.api_clients.protocols import AsyncHttpClient

from .async_http_client import AsyncHTTPClient


@dataclass(frozen=True, slots=True)
class StravaAPIConfig:
    base_url: str = "https://www.strava.com/api/v3"
    content_type: str = "application/json"

    def __post_init__(self) -> None:
        if not isinstance(self.base_url, str):
            raise TypeError("Strava API base URL must be a string.")
        parsed_url = urlsplit(self.base_url)
        if (
            parsed_url.scheme != "https"
            or not parsed_url.hostname
            or parsed_url.username is not None
            or parsed_url.password is not None
            or parsed_url.query
            or parsed_url.fragment
        ):
            raise ValueError("Strava API base URL must be an HTTPS origin and path.")
        if not isinstance(self.content_type, str):
            raise TypeError("Strava API content type must be a string.")
        if not self.content_type.strip():
            raise ValueError("Strava API content type cannot be empty.")
        object.__setattr__(self, "base_url", self.base_url.rstrip("/"))


class AsyncStravaAPI:
    def __init__(
        self,
        access_token: str,
        config: StravaAPIConfig | None = None,
        http_client: AsyncHttpClient | None = None,
    ) -> None:
        if not isinstance(access_token, str):
            raise TypeError("Access token must be a string.")
        if not access_token.strip():
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
        if not isinstance(endpoint, str):
            raise TypeError("Strava API endpoint must be a string.")
        if not endpoint.startswith("/") or endpoint.startswith("//"):
            raise ValueError("Strava API endpoint must be an absolute path.")
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
