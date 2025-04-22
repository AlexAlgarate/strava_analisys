from src.database.supabase_deleter import SupabaseDeleter
from src.encryptor import FernetEncryptor

from ..http.http_clients import AsyncHTTPClient
from .base_strava_api import BaseStravaAPI, StravaAPIConfig


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
                database_deleter=deleter, table=table, encryptor=encryptor
            ),
            config=config,
        )

    async def make_request_async(self, endpoint: str, params: dict = None) -> dict:
        url = self.get_url(endpoint)
        return await self.http_client.get(
            url=url, headers=self.get_headers(), params=params
        )
