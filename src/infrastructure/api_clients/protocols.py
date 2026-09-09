from collections.abc import Mapping
from typing import Protocol


class AsyncHttpClient(Protocol):
    """Minimal HTTP boundary required by the Strava adapter."""

    async def make_async_request(
        self,
        url: str,
        headers: Mapping[str, str],
        params: Mapping[str, str | int] | None = None,
    ) -> object: ...
