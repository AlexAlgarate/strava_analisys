from typing import Any, Dict, cast

from src.infrastructure.database.supabase_deleter import SupabaseDeleter
from src.interfaces.async_http_client import BaseASyncHTTPClient
from src.interfaces.encryptor import IEncryptation
from src.interfaces.strava_api import BaseStravaAPI, StravaAPIConfig

from ..http.async_http_client import AsyncHTTPClient


class AsyncStravaAPI(BaseStravaAPI):
    def __init__(
        self,
        access_token: str,
        table: str,
        encryptor: IEncryptation,
        config: StravaAPIConfig | None = None,
        deleter: SupabaseDeleter | None = None,
    ):
        super().__init__(
            access_token=access_token,
            http_client=AsyncHTTPClient(
                database_deleter=deleter,
                table=table,
                encryptor=encryptor,
            ),
            config=config,
        )

    async def make_request(
        self, endpoint: str, params: dict | None = None
    ) -> Dict[str, Any]:
        url = self.get_url(endpoint)
        headers = self.get_headers()
        client = cast(BaseASyncHTTPClient, self.http_client)

        return await client.make_async_request(
            url=url,
            headers=headers,
            params=params,
        )
