from typing import Dict

import aiohttp
import requests

from src.interfaces.strava_api import InterfaceStravaAPI


class StravaAPI(InterfaceStravaAPI):
    BASE_URL = "https://www.strava.com/api/v3"

    def __init__(self, access_token: str):
        if not access_token:
            raise ValueError("Access token must be provided.")
        self.access_token = access_token

    def _get_headers(self) -> Dict[str, str]:
        """Generate headers for requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _get_url(self, endpoint: str) -> str:
        """Construct full URL for a given endpoint."""
        return f"{self.BASE_URL}{endpoint}"

    def make_request(self, endpoint: str, params: dict = None) -> dict:
        url = self._get_url(endpoint)
        try:
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return {}

    async def make_request_async(self, endpoint: str, params: dict = None) -> dict:
        url = self._get_url(endpoint)
        async with aiohttp.ClientSession(headers=self._get_headers()) as session:
            async with session.get(url, params=params) as response:
                if response.status == 429:
                    raise Exception("Too Many Requests. Wait and try again later.")
                response.raise_for_status()
                if await response.json() == []:
                    raise Exception("No activities found.")
                return await response.json()
