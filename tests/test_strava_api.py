from types import TracebackType
from typing import Self, cast
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest

from src.application.errors import RateLimitExceededError, UnauthorizedError
from src.infrastructure.api_clients.async_http_client import (
    AsyncHTTPClient,
    HTTPClientConfig,
)
from src.infrastructure.api_clients.async_strava_api import (
    AsyncStravaAPI,
    StravaAPIConfig,
)
from src.infrastructure.api_clients.protocols import AsyncHttpClient


class MockResponse:
    def __init__(self, data: object, status: int = 200) -> None:
        self._data = data
        self.status = status

    async def json(self) -> object:
        return self._data

    def raise_for_status(self) -> None:
        if 400 <= self.status < 600:
            raise aiohttp.ClientResponseError(
                request_info=Mock(),
                history=(),
                status=self.status,
            )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        return None


def _session(*responses: MockResponse) -> Mock:
    session = Mock(spec=aiohttp.ClientSession)
    session.closed = False
    session.close = AsyncMock()
    session.get.side_effect = responses
    return session


class TestStravaAPI:
    test_token = "test-token"
    test_config = StravaAPIConfig(
        base_url="https://test.api.com/v3",
        content_type="application/json",
    )

    @pytest.fixture
    def http_client(self) -> Mock:
        client = Mock(spec=AsyncHttpClient)
        client.make_async_request = AsyncMock()
        client.close = AsyncMock()
        return client

    @pytest.fixture
    def async_api(self, http_client: Mock) -> AsyncStravaAPI:
        return AsyncStravaAPI(
            access_token=self.test_token,
            config=self.test_config,
            http_client=http_client,
        )

    def test_get_headers(self, async_api: AsyncStravaAPI) -> None:
        assert async_api.get_headers() == {
            "Authorization": f"Bearer {self.test_token}",
            "Content-Type": "application/json",
        }

    def test_get_url(self, async_api: AsyncStravaAPI) -> None:
        assert async_api.get_url("/athlete") == "https://test.api.com/v3/athlete"

    def test_rejects_empty_access_token(self) -> None:
        with pytest.raises(ValueError, match="Access token"):
            AsyncStravaAPI(access_token="")

    @pytest.mark.asyncio
    async def test_make_request_delegates_to_http_client(
        self,
        async_api: AsyncStravaAPI,
        http_client: Mock,
    ) -> None:
        http_client.make_async_request.return_value = {"id": 12345}

        result = await async_api.make_request("/activities/12345", {"page": 1})

        assert result == {"id": 12345}
        http_client.make_async_request.assert_awaited_once_with(
            url="https://test.api.com/v3/activities/12345",
            headers={
                "Authorization": "Bearer test-token",
                "Content-Type": "application/json",
            },
            params={"page": 1},
        )

    @pytest.mark.asyncio
    async def test_does_not_close_injected_http_client(
        self,
        async_api: AsyncStravaAPI,
        http_client: Mock,
    ) -> None:
        async with async_api:
            pass

        http_client.close.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_closes_owned_http_client(self) -> None:
        http_client = Mock(spec=AsyncHttpClient)
        http_client.close = AsyncMock()
        with patch(
            "src.infrastructure.api_clients.async_strava_api.AsyncHTTPClient",
            return_value=http_client,
        ):
            async with AsyncStravaAPI(access_token="token"):
                pass

        http_client.close.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_http_client_returns_json_and_reuses_session() -> None:
    session = _session(
        MockResponse({"data": "first"}), MockResponse({"data": "second"})
    )
    client = AsyncHTTPClient(session=cast(aiohttp.ClientSession, session))

    first = await client.make_async_request("https://example.test", {})
    second = await client.make_async_request("https://example.test", {})

    assert first == {"data": "first"}
    assert second == {"data": "second"}
    assert session.get.call_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "error_type"),
    [(401, UnauthorizedError), (429, RateLimitExceededError)],
)
async def test_http_client_translates_strava_statuses(
    status: int,
    error_type: type[Exception],
) -> None:
    session = _session(MockResponse({}, status=status))
    client = AsyncHTTPClient(session=cast(aiohttp.ClientSession, session))

    with pytest.raises(error_type):
        await client.make_async_request("https://example.test", {})


@pytest.mark.asyncio
async def test_http_client_retries_server_errors() -> None:
    session = _session(MockResponse({}, status=503), MockResponse({"ok": True}))
    client = AsyncHTTPClient(
        config=HTTPClientConfig(max_attempts=2, retry_backoff_seconds=0),
        session=cast(aiohttp.ClientSession, session),
    )

    result = await client.make_async_request("https://example.test", {})

    assert result == {"ok": True}
    assert session.get.call_count == 2


@pytest.mark.asyncio
async def test_http_client_raises_final_server_error() -> None:
    session = _session(MockResponse({}, status=500), MockResponse({}, status=500))
    client = AsyncHTTPClient(
        config=HTTPClientConfig(max_attempts=2, retry_backoff_seconds=0),
        session=cast(aiohttp.ClientSession, session),
    )

    with pytest.raises(aiohttp.ClientResponseError):
        await client.make_async_request("https://example.test", {})


@pytest.mark.asyncio
async def test_http_client_retries_connection_errors() -> None:
    session = _session()
    session.get.side_effect = [
        aiohttp.ClientConnectionError("offline"),
        MockResponse({"ok": True}),
    ]
    client = AsyncHTTPClient(
        config=HTTPClientConfig(max_attempts=2, retry_backoff_seconds=0),
        session=cast(aiohttp.ClientSession, session),
    )

    assert await client.make_async_request("https://example.test", {}) == {"ok": True}


@pytest.mark.asyncio
async def test_http_client_owns_and_closes_created_session() -> None:
    session = _session()
    with patch("aiohttp.ClientSession", return_value=session) as factory:
        async with AsyncHTTPClient(HTTPClientConfig(timeout_seconds=7)):
            pass

    factory.assert_called_once()
    assert factory.call_args.kwargs["timeout"].total == 7
    session.close.assert_awaited_once_with()


@pytest.mark.parametrize(
    "config",
    [
        HTTPClientConfig(timeout_seconds=1),
        HTTPClientConfig(max_attempts=1),
        HTTPClientConfig(retry_backoff_seconds=0),
    ],
)
def test_accepts_valid_http_configuration(config: HTTPClientConfig) -> None:
    assert config


@pytest.mark.parametrize(
    "kwargs",
    [
        {"timeout_seconds": 0},
        {"max_attempts": 0},
        {"retry_backoff_seconds": -1},
    ],
)
def test_rejects_invalid_http_configuration(kwargs: dict[str, int]) -> None:
    with pytest.raises(ValueError):
        HTTPClientConfig(**kwargs)  # type: ignore[arg-type]
