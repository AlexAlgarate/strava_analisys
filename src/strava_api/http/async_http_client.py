from typing import Any, Dict

import aiohttp

from src.infrastructure.database.supabase_deleter import SupabaseDeleter
from src.interfaces.async_http_client import BaseASyncHTTPClient
from src.interfaces.encryptor import IEncryptation
from src.utils import exceptions

UNAUTHORIZED_USER = 401
REACH_REQUEST_LIMIT = 429


class AsyncHTTPClient(BaseASyncHTTPClient):
    def __init__(
        self,
        database_deleter: SupabaseDeleter | None = None,
        table: str | None = None,
        encryptor: IEncryptation | None = None,
    ):
        self.database_deleter = database_deleter
        self.table = table
        self.encryptor = encryptor

    async def make_async_request(
        self, url, headers: Dict[str, str], params: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == REACH_REQUEST_LIMIT:
                    raise exceptions.TooManyRequestError(
                        "\n\n You have reached the request limit. Please, try again in 15 minutes."
                    )

                if response.status == UNAUTHORIZED_USER:
                    self._remove_expired_tokens()
                    return {}
                return await response.json()

    def _remove_expired_tokens(self):
        if self.database_deleter and self.table and self.encryptor:
            self.database_deleter.cleanup_expired_tokens(
                table=self.table, encryptor=self.encryptor
            )
