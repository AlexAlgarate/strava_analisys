from typing import Any, cast

import aiohttp

from src.interfaces.api_clients.async_http_client import BaseASyncHTTPClient
from src.utils import exceptions

UNAUTHORIZED_USER = 401
REACH_REQUEST_LIMIT = 429


class AsyncHTTPClient(BaseASyncHTTPClient):
    async def make_async_request(
        self,
        url: str,
        headers: dict[str, str],
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        async with (
            aiohttp.ClientSession() as session,
            session.get(url, headers=headers, params=params) as response,
        ):
            if response.status == REACH_REQUEST_LIMIT:
                raise exceptions.TooManyRequestError(
                    "\n\n You have reached the request limit. Please, try again in 15 minutes."
                )

            if response.status == UNAUTHORIZED_USER:
                raise exceptions.UnauthorizedError(
                    "Strava rejected the access token. Reauthorize the application."
                )
            response.raise_for_status()
            return cast(dict[str, Any], await response.json())
