from typing import Any, Dict

import aiohttp

from src.database.supabase_deleter import SupabaseDeleter
from src.encryptor import FernetEncryptor
from src.interfaces.async_http_client import BaseASyncHTTPClient
from src.utils import exceptions


class AsyncHTTPClient(BaseASyncHTTPClient):
    def __init__(
        self,
        database_deleter: SupabaseDeleter | None = None,
        table: str | None = None,
        encryptor: FernetEncryptor | None = None,
    ):
        self.database_deleter = database_deleter
        self.table = table
        self.encryptor = encryptor

    async def get_method(
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
