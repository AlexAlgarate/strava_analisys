from unittest.mock import patch

import pytest
import requests
from aioresponses import aioresponses

from src.strava_api import StravaAPI

ACCESS_TOKEN = "test_token"


class TestStravaAPI:
    @pytest.fixture
    def strava_api(self):
        return StravaAPI(access_token=ACCESS_TOKEN)

    def test_init_without_token(self):
        with pytest.raises(ValueError, match="Access token must be provided."):
            StravaAPI("")

    def test_init_with_token(self):
        api = StravaAPI(ACCESS_TOKEN)
        assert api.access_token == ACCESS_TOKEN

    def test_get_headers(self, strava_api):
        headers = strava_api._get_headers()
        assert headers == {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

    def test_get_url(self, strava_api):
        endpoint = "/athlete"
        expected_url = f"https://www.strava.com/api/v3{endpoint}"
        assert strava_api._get_url(endpoint) == expected_url

    @patch("requests.get")
    def test_make_request(self, mock_get, strava_api):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 12345, "name": "Test Athlete"}

        response = strava_api.make_request("/athlete")
        assert response == {"id": 12345, "name": "Test Athlete"}
        mock_get.assert_called_once_with(
            "https://www.strava.com/api/v3/athlete",
            headers=strava_api._get_headers(),
            params=None,
        )

    @patch("requests.get")
    def test_make_request_error(self, mock_get, strava_api):
        mock_get.side_effect = requests.exceptions.RequestException("API error")
        response = strava_api.make_request("/athlete")
        assert response == {}  # Should return an empty dict

    @pytest.mark.asyncio
    async def test_make_request_async(self, strava_api):
        endpoint = "/activities/12345"
        url = f"https://www.strava.com/api/v3{endpoint}"
        mock_response = {"id": 12345, "name": "Test Activity"}

        with aioresponses() as m:
            m.get(url, payload=mock_response)

            response = await strava_api.make_request_async(endpoint)
            assert response == mock_response

    @pytest.mark.asyncio
    async def test_make_request_async_too_many_requests(self, strava_api):
        endpoint = "/activities/12345"
        url = f"https://www.strava.com/api/v3{endpoint}"

        with aioresponses() as m:
            m.get(url, status=429)

            with pytest.raises(
                Exception, match="Too Many Requests. Wait and try again later."
            ):
                await strava_api.make_request_async(endpoint)
