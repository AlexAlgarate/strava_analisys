from typing import Dict

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
                database_deleter=deleter, table=table, encryptor=encryptor
            ),
            config=config,
        )

    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": self.config.content_type,
        }

    async def make_request_async(self, endpoint: str, params: dict = None) -> dict:
        url = self.get_url(endpoint)
        headers = self.get_headers()

        return await self.http_client.get(url=url, headers=headers, params=params)
