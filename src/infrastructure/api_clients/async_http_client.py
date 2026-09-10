import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from math import isfinite
from types import TracebackType
from typing import Self, cast

import aiohttp

from src.application.errors import (
    ExternalServiceResponseError,
    ExternalServiceUnavailableError,
    InactiveApplicationError,
    InvalidExternalDataError,
    RateLimitExceededError,
    UnauthorizedError,
)

UNAUTHORIZED_USER = 401
FORBIDDEN = 403
RATE_LIMIT_EXCEEDED = 429
INACTIVE_APPLICATION_ERROR = {
    "resource": "Application",
    "field": "Status",
    "code": "Inactive",
}


@dataclass(frozen=True, slots=True)
class HTTPClientConfig:
    timeout_seconds: float = 15.0
    max_attempts: int = 3
    retry_backoff_seconds: float = 0.25

    def __post_init__(self) -> None:
        _validate_duration("timeout", self.timeout_seconds, allow_zero=False)
        if isinstance(self.max_attempts, bool) or not isinstance(
            self.max_attempts, int
        ):
            raise TypeError("HTTP max attempts must be an integer.")
        if self.max_attempts < 1:
            raise ValueError("HTTP max attempts must be at least one.")
        _validate_duration(
            "retry backoff",
            self.retry_backoff_seconds,
            allow_zero=True,
        )


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
            except (
                aiohttp.ClientConnectionError,
                aiohttp.ClientPayloadError,
                TimeoutError,
            ) as error:
                if attempt == self._config.max_attempts:
                    raise ExternalServiceUnavailableError(
                        "Could not reach Strava after retrying."
                    ) from error
            except aiohttp.ClientResponseError as error:
                if error.status < 500 or attempt == self._config.max_attempts:
                    raise ExternalServiceResponseError(
                        f"Strava returned unexpected HTTP status {error.status}.",
                        status_code=error.status,
                    ) from error

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
            allow_redirects=False,
        ) as response:
            if 300 <= response.status < 400:
                raise ExternalServiceResponseError(
                    f"Strava returned unexpected HTTP status {response.status}.",
                    status_code=response.status,
                )
            if response.status == RATE_LIMIT_EXCEEDED:
                raise RateLimitExceededError(
                    "You have reached the request limit. Please try again later."
                )
            if response.status == UNAUTHORIZED_USER:
                raise UnauthorizedError(
                    "Strava rejected the access token. Reauthorize the application."
                )
            if response.status == FORBIDDEN and await _reports_inactive_application(
                response
            ):
                raise InactiveApplicationError(
                    "Strava reports that this API application is inactive. Check its "
                    "status and subscription at https://www.strava.com/settings/api, "
                    "then reactivate it or contact Strava support. Reauthorize after "
                    "it is active."
                )
            response.raise_for_status()
            try:
                return cast(object, await response.json())
            except (aiohttp.ContentTypeError, ValueError) as error:
                raise InvalidExternalDataError(
                    "Strava returned a response that is not valid JSON."
                ) from error

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self._config.timeout_seconds)
            )
            self._owns_session = True
        return self._session


async def _reports_inactive_application(response: aiohttp.ClientResponse) -> bool:
    try:
        payload = await response.json()
    except (aiohttp.ContentTypeError, ValueError):
        return False

    if not isinstance(payload, Mapping):
        return False

    errors = payload.get("errors")
    if not isinstance(errors, list):
        return False

    return any(_is_inactive_application_error(error) for error in errors)


def _is_inactive_application_error(error: object) -> bool:
    return isinstance(error, Mapping) and all(
        error.get(field) == expected
        for field, expected in INACTIVE_APPLICATION_ERROR.items()
    )


def _validate_duration(name: str, value: object, *, allow_zero: bool) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"HTTP {name} must be numeric.")
    try:
        finite = isfinite(value)
    except OverflowError as error:
        raise ValueError(f"HTTP {name} must be finite.") from error
    if not finite:
        raise ValueError(f"HTTP {name} must be finite.")
    if value < 0 or (not allow_zero and value == 0):
        qualifier = "non-negative" if allow_zero else "positive"
        raise ValueError(f"HTTP {name} must be {qualifier}.")
