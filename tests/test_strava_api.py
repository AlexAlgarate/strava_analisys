import pytest
import requests
from aioresponses import aioresponses

from src.strava_api import StravaAPI


class TestStravaAPI:
    @pytest.fixture
    def strava_api(self):
        return StravaAPI(access_token="test_token")

    def test_make_request(self, strava_api, requests_mock):
        endpoint = "/activities/12345"
        url = f"https://www.strava.com/api/v3{endpoint}"
        mock_response = {"id": 12345, "name": "Test Activity"}

        requests_mock.get(url, json=mock_response)

        response = strava_api.make_request(endpoint)
        assert response == mock_response

    @pytest.mark.asyncio
    async def test_make_request_async(self, strava_api):
        endpoint = "/activities/12345"
        url = f"https://www.strava.com/api/v3{endpoint}"
        mock_response = {"id": 12345, "name": "Test Activity"}

        with aioresponses() as m:
            m.get(url, payload=mock_response)

            response = await strava_api.make_request_async(endpoint)
            assert response == mock_response

    def test_make_request_too_many_requests(self, strava_api, requests_mock):
        endpoint = "/activities/12345"
        url = f"https://www.strava.com/api/v3{endpoint}"

        requests_mock.get(url, status_code=429)

        with pytest.raises(
            Exception, match="Too Many Requests. Wait and try again later."
        ):
            strava_api.make_request(endpoint)

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
