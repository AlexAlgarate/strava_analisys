from typing import Any, Dict, Optional

import aiohttp
import requests

from src.database.supabase_deleter import SupabaseDeleter
from src.encryptor import FernetEncryptor
from src.utils import exceptions

from .base_http_client import BaseHTTPClient


class SyncHTTPClient(BaseHTTPClient):
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
    def __init__(
        self,
        database_deleter: Optional[SupabaseDeleter] = None,
        table: Optional[str] = None,
        encryptor: Optional[FernetEncryptor] = None,
    ):
        self.database_deleter = database_deleter
        self.table = table
        self.encryptor = encryptor

    async def get(
        self, url: str, headers: Dict[str, str], params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 429:
                    raise exceptions.TooManyRequestError(
                        "\n\nToo Many Requests. Wait and try again later."
                    )
                if response.status == 401:
                    if self.database_deleter and self.table and self.encryptor:
                        self.database_deleter.cleanup_expired_tokens(
                            table=self.table, encryptor=self.encryptor
                        )
                    return {}
                return await response.json()
