from typing import Dict

import aiohttp
import requests

from src.interfaces.strava_api import AsyncStravaAPI, SyncStravaAPI
from src.utils import exceptions as exception


class StravaAPI(SyncStravaAPI, AsyncStravaAPI):
    BASE_URL = "https://www.strava.com/api/v3"

    def __init__(self, access_token: str):
        if not access_token:
            raise ValueError("\n\nAccess token must be provided.")
        self.access_token = access_token

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _get_url(self, endpoint: str) -> str:
        return f"{self.BASE_URL}{endpoint}"

    def make_request(self, endpoint: str, params: dict = None) -> dict:
        url = self._get_url(endpoint)
        try:
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"\n\nError making request to {url}: {e}")
            return {}

    async def make_request_async(self, endpoint: str, params: dict = None) -> dict:
        url = self._get_url(endpoint)
        async with aiohttp.ClientSession(headers=self._get_headers()) as session:
            async with session.get(url, params=params) as response:
                if response.status == 429:
                    raise exception.TooManyRequestError(
                        "\n\nToo Many Requests. Wait and try again later."
                    )
                response.raise_for_status()
                if response.status == 401:
                    raise exception.UnauthorizedError(
                        "\n\nUnauthorized. Check your token."
                    )
                if await response.json() == []:
                    raise exception.NotActivitiesError("\n\nNo activities found.")
                return await response.json()
