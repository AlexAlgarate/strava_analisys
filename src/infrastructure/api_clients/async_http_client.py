import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from types import TracebackType
from typing import Self, cast

import aiohttp

from src.application.errors import RateLimitExceededError, UnauthorizedError

UNAUTHORIZED_USER = 401
REACH_REQUEST_LIMIT = 429


@dataclass(frozen=True, slots=True)
class HTTPClientConfig:
    timeout_seconds: float = 15.0
    max_attempts: int = 3
    retry_backoff_seconds: float = 0.25

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("HTTP timeout must be positive.")
        if self.max_attempts < 1:
            raise ValueError("HTTP max attempts must be at least one.")
        if self.retry_backoff_seconds < 0:
            raise ValueError("HTTP retry backoff cannot be negative.")


class AsyncHTTPClient:
    def __init__(
        self,
        config: HTTPClientConfig | None = None,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._config = config or HTTPClientConfig()
        self._session = session
        self._owns_session = session is None

    async def __aenter__(self) -> Self:
        self._get_session()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        if (
            self._owns_session
            and self._session is not None
            and not self._session.closed
        ):
            await self._session.close()

    async def make_async_request(
        self,
        url: str,
        headers: Mapping[str, str],
        params: Mapping[str, str | int] | None = None,
    ) -> object:
        for attempt in range(1, self._config.max_attempts + 1):
            try:
                return await self._request_once(url, headers, params)
            except (aiohttp.ClientConnectionError, TimeoutError):
                if attempt == self._config.max_attempts:
                    raise
            except aiohttp.ClientResponseError as error:
                if error.status < 500 or attempt == self._config.max_attempts:
                    raise

            await asyncio.sleep(self._config.retry_backoff_seconds * attempt)

        raise RuntimeError("HTTP retry loop completed without a result.")

    async def _request_once(
        self,
        url: str,
        headers: Mapping[str, str],
        params: Mapping[str, str | int] | None,
    ) -> object:
        async with self._get_session().get(
            url,
            headers=headers,
            params=params,
        ) as response:
            if response.status == REACH_REQUEST_LIMIT:
                raise RateLimitExceededError(
                    "You have reached the request limit. Please try again later."
                )
            if response.status == UNAUTHORIZED_USER:
                raise UnauthorizedError(
                    "Strava rejected the access token. Reauthorize the application."
                )
            response.raise_for_status()
            return cast(object, await response.json())

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self._config.timeout_seconds)
            )
            self._owns_session = True
        return self._session
