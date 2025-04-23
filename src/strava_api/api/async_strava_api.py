from src.database.supabase_deleter import SupabaseDeleter
from src.encryptor import FernetEncryptor
from src.interfaces.strava_api import BaseStravaAPI, StravaAPIConfig

from ..http.http_clients import AsyncHTTPClient


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

    # def make_request(self, endpoint, params=None): ...
    async def make_request(self, endpoint: str, params: dict = None) -> dict:
        url = self.get_url(endpoint)
        headers = self.get_headers()

        return await self.http_client.get_method(
            url=url,
            headers=headers,
            params=params,
        )
