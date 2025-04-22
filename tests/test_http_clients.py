"""from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest
import requests

from src.strava_api.http.http_clients import AsyncHTTPClient, SyncHTTPClient
from src.utils.exceptions import TooManyRequestError


class TestSyncHTTPClient:
    @pytest.fixture
    def sync_client(self):
        return SyncHTTPClient()

    def test_get_success(self, sync_client):
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.status_code = 200

        with patch("requests.get", return_value=mock_response) as mock_get:
            result = sync_client.get(
                url="http://test.com",
                headers={"Authorization": "Bearer test"},
                params={"param": "value"},
            )

            assert result == {"data": "test"}
            mock_get.assert_called_once_with(
                "http://test.com",
                headers={"Authorization": "Bearer test"},
                params={"param": "value"},
            )

    def test_get_unauthorized(self, sync_client):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=Mock(status_code=401)
        )

        with patch("requests.get", return_value=mock_response):
            result = sync_client.get(
                url="http://test.com",
                headers={"Authorization": "Bearer test"},
            )
            assert result == {}

    def test_get_request_exception(self, sync_client):
        with patch("requests.get", side_effect=requests.exceptions.RequestException):
            result = sync_client.get(
                url="http://test.com",
                headers={"Authorization": "Bearer test"},
            )
            assert result == {}


class TestAsyncHTTPClient:
    @pytest.fixture
    def mock_response(self):
        response = AsyncMock()
        response.__aenter__.return_value = response
        return response

    @pytest.fixture
    def mock_session(self, mock_response):
        session = AsyncMock()
        session.__aenter__.return_value = session
        session.get.return_value = mock_response
        return session

    @pytest.fixture
    def mock_database_deleter(self):
        return Mock()

    @pytest.fixture
    def mock_encryptor(self):
        return Mock()

    @pytest.fixture
    def async_client_with_deps(self, mock_database_deleter, mock_encryptor):
        return AsyncHTTPClient(
            database_deleter=mock_database_deleter,
            table="test_table",
            encryptor=mock_encryptor,
        )

    @pytest.fixture
    def async_client_no_deps(self):
        return AsyncHTTPClient()

    @pytest.mark.asyncio
    async def test_get_success(self, async_client_no_deps, mock_session, mock_response):
        mock_response.status = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.json = AsyncMock(return_value={"data": "test"})

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await async_client_no_deps.get(
                url="http://test.com",
                headers={"Authorization": "Bearer test"},
                params={"param": "value"},
            )

            assert result == {"data": "test"}
            mock_session.get.assert_called_once_with(
                "http://test.com",
                headers={"Authorization": "Bearer test"},
                params={"param": "value"},
            )

    @pytest.mark.asyncio
    async def test_get_too_many_requests(
        self, async_client_no_deps, mock_session, mock_response
    ):
        mock_response.status = 429

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with pytest.raises(TooManyRequestError):
                await async_client_no_deps.get(
                    url="http://test.com",
                    headers={"Authorization": "Bearer test"},
                )

    @pytest.mark.asyncio
    async def test_get_unauthorized_with_cleanup(
        self,
        async_client_with_deps,
        mock_database_deleter,
        mock_encryptor,
        mock_session,
        mock_response,
    ):
        mock_response.status = 401

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await async_client_with_deps.get(
                url="http://test.com",
                headers={"Authorization": "Bearer test"},
            )

            assert result == {}
            mock_database_deleter.cleanup_expired_tokens.assert_called_once_with(
                table="test_table", encryptor=mock_encryptor
            )

    @pytest.mark.asyncio
    async def test_get_unauthorized_no_cleanup(
        self, async_client_no_deps, mock_session, mock_response
    ):
        mock_response.status = 401

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await async_client_no_deps.get(
                url="http://test.com",
                headers={"Authorization": "Bearer test"},
            )

            assert result == {}

    @pytest.mark.asyncio
    async def test_get_client_error(self, async_client_no_deps, mock_session):
        mock_session.get.side_effect = aiohttp.ClientError()

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with pytest.raises(aiohttp.ClientError):
                await async_client_no_deps.get(
                    url="http://test.com",
                    headers={"Authorization": "Bearer test"},
                )
"""
