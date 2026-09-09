from collections.abc import Mapping
from typing import Protocol


class StravaAPI(Protocol):
    """Asynchronous boundary for the Strava API."""

    async def make_request(
        self,
        endpoint: str,
        params: Mapping[str, str | int] | None = None,
    ) -> object: ...
