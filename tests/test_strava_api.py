from typing import Any, Optional, Type
from unittest.mock import Mock, patch

import aiohttp
import pytest

from src.interfaces.database.database_deleter import IDatabaseDeleter
from src.interfaces.encryptor import IEncryptation
from src.interfaces.strava_api import StravaAPIConfig
from src.strava_api.api.async_strava_api import AsyncStravaAPI
from src.utils import exceptions


class MockResponse:
    def __init__(self, data: Any, status: int = 200) -> None:
        self._data = data
        self.status = status

    async def json(self) -> Any:
        return self._data

    def raise_for_status(self) -> None:
        if 400 <= self.status < 600:
            raise aiohttp.ClientResponseError(
                request_info=None,  # type: ignore
                history=None,  # type: ignore
                status=self.status,
            )

    async def __aenter__(self) -> "MockResponse":
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        pass


class TestStravaAPI:
    TEST_TOKEN = "test_token"
    TEST_TABLE = "test_table"
    TEST_ENCRYPTOR = Mock(spec=IEncryptation)
    TEST_DELETER = Mock(spec=IDatabaseDeleter)
    TEST_CONFIG = StravaAPIConfig(
        base_url="https://test.api.com/v3", content_type="application/json"
    )

    @pytest.fixture
    def async_api(self) -> AsyncStravaAPI:
        return AsyncStravaAPI(
            access_token=self.TEST_TOKEN,
            config=self.TEST_CONFIG,
            table=self.TEST_TABLE,
            encryptor=self.TEST_ENCRYPTOR,
            deleter=self.TEST_DELETER,
        )

    def test_get_headers(self, async_api: AsyncStravaAPI) -> None:
        headers = async_api.get_headers()
        assert headers == {
            "Authorization": f"Bearer {self.TEST_TOKEN}",
            "Content-Type": "application/json",
        }

    def test_get_url(self, async_api: AsyncStravaAPI) -> None:
        endpoint = "/athlete"
        expected_url = f"{self.TEST_CONFIG.base_url}{endpoint}"
        assert async_api.get_url(endpoint) == expected_url

    @pytest.mark.asyncio
    async def test_make_request_async(self, async_api: AsyncStravaAPI) -> None:
        endpoint = "/activities/12345"
        mock_response = {"id": 12345, "name": "Test Activity"}

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value = MockResponse(mock_response)
            response = await async_api.make_request(endpoint)
            assert response == mock_response

    @pytest.mark.asyncio
    async def test_make_request_async_too_many_requests(
        self, async_api: AsyncStravaAPI
    ) -> None:
        endpoint = "/activities/12345"

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value = MockResponse({}, status=429)
            with pytest.raises(exceptions.TooManyRequestError):
                await async_api.make_request(endpoint)
