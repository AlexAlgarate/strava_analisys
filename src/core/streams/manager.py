from src.core.activities.fetchers import WeeklyActivitiesFetcher
from src.core.concurrency import DEFAULT_MAX_CONCURRENCY
from src.core.ports.strava import StravaAPI
from src.core.streams.fetcher import ActivityStreamsFetcher
from src.domain.activity_stream import ActivityStream, StreamBatch
from src.utils import constants as constant


class StreamManager:
    """Manages stream data operations and fetching."""

    def __init__(
        self,
        api: StravaAPI,
        *,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    ) -> None:
        self._api = api
        self._max_concurrency = max_concurrency

    async def get_streams_for_activity(self, activity_id: int) -> ActivityStream:
        """Get detailed stream data for a specific activity."""
        return await ActivityStreamsFetcher(
            api=self._api, activity_id=activity_id
        ).fetch_activity_data(stream_keys=constant.ACTIVITY_STREAMS_KEYS)

    async def get_streams_for_multiple_activities(
        self, activity_ids: list[int]
    ) -> StreamBatch:
        """Get detailed stream data for multiple activities."""
        return await ActivityStreamsFetcher.fetch_multiple_activities_streams(
            api=self._api,
            list_id_activities=activity_ids,
            stream_keys=constant.ACTIVITY_STREAMS_KEYS,
            max_concurrency=self._max_concurrency,
        )

    async def get_weekly_streams(self, previous_week: bool) -> StreamBatch:
        """Fetch streams for activities in the selected week."""
        week_fetcher = WeeklyActivitiesFetcher(self._api)
        activities = await week_fetcher.fetch_activity_data(previous_week=previous_week)
        ids = [activity.id for activity in activities]
        return await ActivityStreamsFetcher.fetch_multiple_activities_streams(
            api=self._api,
            list_id_activities=ids,
            stream_keys=constant.ACTIVITY_STREAMS_KEYS,
            max_concurrency=self._max_concurrency,
        )
