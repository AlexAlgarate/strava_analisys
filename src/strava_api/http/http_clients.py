"""HTTP client implementations for Strava API."""

from typing import Any, Dict

import aiohttp
import requests

from src.utils import exceptions

from .base_http_client import BaseHTTPClient


class SyncHTTPClient(BaseHTTPClient):
    """Synchronous HTTP client implementation using requests."""

    def get(
        self, url: str, headers: Dict[str, str], params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            if response.status_code == 401:
                raise exceptions.UnauthorizedError(
                    "\n\nUnauthorized. Check your token."
                )
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"\n\nError making request to {url}: {e}")
            print("Deleting token from Supabase.")
            return {}


class AsyncHTTPClient(BaseHTTPClient):
    """Asynchronous HTTP client implementation using aiohttp."""

    async def get(
        self, url: str, headers: Dict[str, str], params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 429:
                    raise exceptions.TooManyRequestError(
                        "\n\nToo Many Requests. Wait and try again later."
                    )
                response.raise_for_status()
                if response.status == 401:
                    raise exceptions.UnauthorizedError(
                        "\n\nUnauthorized. Check your token."
                    )
                return await response.json()
