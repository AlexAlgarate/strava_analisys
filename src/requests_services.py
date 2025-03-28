from typing import Any, Dict

import aiohttp
import requests

from src.interfaces.strava_api import HTTPClient
from src.utils import exceptions as exception


class RequestHTTPClient(HTTPClient):
    def get(
        self, url: str, headers: Dict[str, str], params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            if response.status_code == 401:
                raise exception.UnauthorizedError("\n\nUnauthorized. Check your token.")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"\n\nError making request to {url}: {e}")
            return {}


class AioHTTPClient(HTTPClient):
    async def get(
        self, url: str, headers: Dict[str, str], params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 429:
                    raise exception.TooManyRequestError(
                        "\n\nToo Many Requests. Wait and try again later."
                    )
                response.raise_for_status()
                if response.status == 401:
                    raise exception.UnauthorizedError(
                        "\n\nUnauthorized. Check your token."
                    )
                data = await response.json()
                if data == []:
                    raise exception.NotActivitiesError("\n\nNo activities found.")
                return data
