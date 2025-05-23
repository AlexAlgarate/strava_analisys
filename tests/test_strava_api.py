from unittest.mock import patch

import aiohttp
import pytest

from src.interfaces.strava_api import StravaAPIConfig
from src.strava_api.api.async_strava_api import AsyncStravaAPI
from src.utils import exceptions


class MockResponse:
    def __init__(self, data, status=200):
        self._data = data
        self.status = status

    async def json(self):
        return self._data

    def raise_for_status(self):
        if 400 <= self.status < 600:
            raise aiohttp.ClientResponseError(
                request_info=None, history=None, status=self.status
            )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class TestStravaAPI:
    TEST_TOKEN = "test_token"
    TEST_TABLE = "test_table"
    TEST_ENCRYPTOR = "test_encryptor"
    TEST_DELETER = "test_deleter"
    TEST_CONFIG = StravaAPIConfig(
        base_url="https://test.api.com/v3", content_type="application/json"
    )

    @pytest.fixture
    def async_api(self):
        return AsyncStravaAPI(
            access_token=self.TEST_TOKEN,
            config=self.TEST_CONFIG,
            table=self.TEST_TABLE,
            encryptor=self.TEST_ENCRYPTOR,
            deleter=self.TEST_DELETER,
        )

    def test_get_headers(self, async_api):
        headers = async_api.get_headers()
        assert headers == {
            "Authorization": f"Bearer {self.TEST_TOKEN}",
            "Content-Type": "application/json",
        }

    def test_get_url(self, async_api):
        endpoint = "/athlete"
        expected_url = f"{self.TEST_CONFIG.base_url}{endpoint}"
        assert async_api.get_url(endpoint) == expected_url

    @pytest.mark.asyncio
    async def test_make_request_async(self, async_api):
        endpoint = "/activities/12345"
        mock_response = {"id": 12345, "name": "Test Activity"}

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value = MockResponse(mock_response)
            response = await async_api.make_request(endpoint)
            assert response == mock_response

    @pytest.mark.asyncio
    async def test_make_request_async_too_many_requests(self, async_api):
        endpoint = "/activities/12345"

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.return_value = MockResponse({}, status=429)
            with pytest.raises(exceptions.TooManyRequestError):
                await async_api.make_request(endpoint)
