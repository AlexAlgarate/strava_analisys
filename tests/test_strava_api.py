from types import TracebackType
from typing import Any, Self
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest

from src.infrastructure.api_clients.async_http_client import AsyncHTTPClient
from src.infrastructure.api_clients.async_strava_api import (
    AsyncStravaAPI,
    StravaAPIConfig,
)
from src.infrastructure.api_clients.protocols import AsyncHttpClient
from src.utils.exceptions import TooManyRequestError, UnauthorizedError


class MockResponse:
    def __init__(self, data: Any, status: int = 200) -> None:
        self._data = data
        self.status = status

    async def json(self) -> Any:
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


class TestStravaAPI:
    TEST_TOKEN = "test-token"
    TEST_CONFIG = StravaAPIConfig(
        base_url="https://test.api.com/v3", content_type="application/json"
    )

    @pytest.fixture
    def http_client(self) -> Mock:
        client = Mock(spec=AsyncHttpClient)
        client.make_async_request = AsyncMock()
        return client

    @pytest.fixture
    def async_api(self, http_client: Mock) -> AsyncStravaAPI:
        return AsyncStravaAPI(
            access_token=self.TEST_TOKEN,
            config=self.TEST_CONFIG,
            http_client=http_client,
        )

    def test_get_headers(self, async_api: AsyncStravaAPI) -> None:
        assert async_api.get_headers() == {
            "Authorization": f"Bearer {self.TEST_TOKEN}",
            "Content-Type": "application/json",
        }

    def test_get_url(self, async_api: AsyncStravaAPI) -> None:
        assert async_api.get_url("/athlete") == "https://test.api.com/v3/athlete"

    def test_rejects_empty_access_token(self) -> None:
        with pytest.raises(ValueError, match="Access token"):
            AsyncStravaAPI(access_token="")

    @pytest.mark.asyncio
    async def test_make_request_delegates_to_http_client(
        self, async_api: AsyncStravaAPI, http_client: Mock
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
async def test_http_client_returns_json() -> None:
    with patch("aiohttp.ClientSession.get") as get:
        get.return_value = MockResponse({"data": "value"})

        result = await AsyncHTTPClient().make_async_request(
            "https://example.test", {"Authorization": "Bearer token"}
        )

    assert result == {"data": "value"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "error_type"),
    [(401, UnauthorizedError), (429, TooManyRequestError)],
)
async def test_http_client_translates_strava_statuses(
    status: int, error_type: type[Exception]
) -> None:
    with patch("aiohttp.ClientSession.get") as get:
        get.return_value = MockResponse({}, status=status)

        with pytest.raises(error_type):
            await AsyncHTTPClient().make_async_request(
                "https://example.test", {"Authorization": "Bearer token"}
            )


@pytest.mark.asyncio
async def test_http_client_raises_other_http_errors() -> None:
    with patch("aiohttp.ClientSession.get") as get:
        get.return_value = MockResponse({}, status=500)

        with pytest.raises(aiohttp.ClientResponseError):
            await AsyncHTTPClient().make_async_request(
                "https://example.test", {"Authorization": "Bearer token"}
            )
