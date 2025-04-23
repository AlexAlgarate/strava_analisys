from unittest.mock import patch

import aiohttp
import pytest

from src.interfaces.strava_api import StravaAPIConfig
from src.strava_api.api.async_strava_api import AsyncStravaAPI
from src.strava_api.api.sync_strava_api import SyncStravaAPI
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
    def sync_api(self):
        return SyncStravaAPI(access_token=self.TEST_TOKEN, config=self.TEST_CONFIG)

    @pytest.fixture
    def async_api(self):
        return AsyncStravaAPI(
            access_token=self.TEST_TOKEN,
            config=self.TEST_CONFIG,
            table=self.TEST_TABLE,
            encryptor=self.TEST_ENCRYPTOR,
            deleter=self.TEST_DELETER,
        )

    def test_init_without_token(self):
        with pytest.raises(ValueError, match="Access token must be provided."):
            SyncStravaAPI("")

    def test_init_with_token(self):
        api = SyncStravaAPI(self.TEST_TOKEN)
        assert api.access_token == self.TEST_TOKEN

    def test_get_headers(self, sync_api):
        headers = sync_api.get_headers()
        assert headers == {
            "Authorization": f"Bearer {self.TEST_TOKEN}",
            "Content-Type": "application/json",
        }

    def test_get_url(self, sync_api):
        endpoint = "/athlete"
        expected_url = f"{self.TEST_CONFIG.base_url}{endpoint}"
        assert sync_api.get_url(endpoint) == expected_url

    @patch("src.strava_api.http.http_clients.requests.get")
    def test_make_request_sync(self, mock_get, sync_api):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 12345, "name": "Test Athlete"}

        response = sync_api.make_request("/athlete")
        assert response == {"id": 12345, "name": "Test Athlete"}
        mock_get.assert_called_once_with(
            f"{self.TEST_CONFIG.base_url}/athlete",
            headers=sync_api.get_headers(),
            params=None,
        )

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
