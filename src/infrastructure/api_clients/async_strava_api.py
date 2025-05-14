from typing import Any, Dict, cast

from src.interfaces.api_clients.async_http_client import BaseASyncHTTPClient
from src.interfaces.api_clients.strava_api import BaseStravaAPI, StravaAPIConfig
from src.interfaces.database.database_deleter import IDatabaseDeleter
from src.interfaces.encryption.encryptor import IEncryptation

from .async_http_client import AsyncHTTPClient


class AsyncStravaAPI(BaseStravaAPI):
    def __init__(
        self,
        access_token: str,
        table: str,
        encryptor: IEncryptation,
        config: StravaAPIConfig | None = None,
        deleter: IDatabaseDeleter | None = None,
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
