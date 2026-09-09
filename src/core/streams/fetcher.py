from src.core.concurrency import DEFAULT_MAX_CONCURRENCY, map_concurrently
from src.core.ports.strava import StravaAPI
from src.domain.activity_stream import (
    ActivityStream,
    StreamBatch,
    StreamFetchFailure,
)
from src.infrastructure.strava.stream_mapper import map_activity_stream


class ActivityStreamsFetcher:
    """Fetches activity stream data from Strava API."""

    def __init__(self, api: StravaAPI, activity_id: int) -> None:
        if isinstance(activity_id, bool) or not isinstance(activity_id, int):
            raise TypeError("Activity ID must be an integer.")
        if activity_id <= 0:
            raise ValueError("Activity ID must be a positive integer.")
        self._api = api
        self._activity_id = activity_id

    async def fetch_activity_data(self, stream_keys: list[str]) -> ActivityStream:
        """Fetch and validate stream data for a single activity."""
        params = {"keys": ",".join(stream_keys), "key_by_type": "true"}
        response = await self._api.make_request(
            f"/activities/{self._activity_id}/streams", params
        )
        return map_activity_stream(self._activity_id, response)

    @classmethod
    async def fetch_multiple_activities_streams(
        cls,
        api: StravaAPI,
        list_id_activities: list[int],
        stream_keys: list[str],
        *,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    ) -> StreamBatch:
        """Fetch streams concurrently while retaining every partial failure."""

        async def fetch_one(
            activity_id: int,
        ) -> ActivityStream | StreamFetchFailure:
            try:
                return await cls(
                    api=api,
                    activity_id=activity_id,
                ).fetch_activity_data(stream_keys=stream_keys)
            except Exception as error:  # noqa: BLE001 - batch boundary records failures
                return StreamFetchFailure(
                    activity_id=activity_id,
                    error_type=type(error).__name__,
                    message=str(error) or "Unknown stream fetch error",
                )

        results = await map_concurrently(
            list_id_activities,
            fetch_one,
            max_concurrency=max_concurrency,
        )
        return StreamBatch(
            streams=tuple(
                result for result in results if isinstance(result, ActivityStream)
            ),
            failures=tuple(
                result for result in results if isinstance(result, StreamFetchFailure)
            ),
        )
