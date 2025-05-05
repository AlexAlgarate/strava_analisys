from typing import Any, Dict, cast

from src.database.supabase_deleter import SupabaseDeleter
from src.infrastructure.encryption.encryptor import FernetEncryptor
from src.interfaces.async_http_client import BaseASyncHTTPClient
from src.interfaces.strava_api import BaseStravaAPI, StravaAPIConfig

from ..http.async_http_client import AsyncHTTPClient


class AsyncStravaAPI(BaseStravaAPI):
    def __init__(
        self,
        access_token: str,
        table: str,
        encryptor: FernetEncryptor,
        config: StravaAPIConfig = None,
        deleter: SupabaseDeleter = None,
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

    async def make_request(self, endpoint: str, params: dict = None) -> Dict[str, Any]:
        url = self.get_url(endpoint)
        headers = self.get_headers()
        client = cast(BaseASyncHTTPClient, self.http_client)

        return await client.get_method(
            url=url,
            headers=headers,
            params=params,
        )
