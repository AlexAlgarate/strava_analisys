import pandas as pd

from src.activities.detailed_activities import WeeklyActivitiesFetcher
from src.core.activities.utils import get_activity_ids
from src.core.streams.fetcher import ActivityStreamsFetcher
from src.infrastructure.api_clients.async_strava_api import AsyncStravaAPI
from src.utils import constants as constant


class StreamManager:
    """Manages stream data operations and fetching."""

    def __init__(self, api_async: AsyncStravaAPI):
        self.api_async = api_async

    async def get_streams_for_activity(self, activity_id: int) -> pd.DataFrame:
        """Get detailed stream data for a specific activity."""
        return await ActivityStreamsFetcher(
            api=self.api_async, id_activity=activity_id
        ).fetch_activity_data(stream_keys=constant.ACTIVITY_STREAMS_KEYS)

    async def get_streams_for_multiple_activities(
        self, activity_ids: list[int]
    ) -> pd.DataFrame:
        """Get detailed stream data for multiple activities."""
        return await ActivityStreamsFetcher.fetch_multiple_activities_streams(
            api=self.api_async,
            list_id_activities=activity_ids,
            stream_keys=constant.ACTIVITY_STREAMS_KEYS,
        )

    async def get_weekly_streams(self, previous_week: bool) -> pd.DataFrame:
        """Fetch streams for activities in the selected week."""
        week_fetcher = WeeklyActivitiesFetcher(self.api_async)
        activities = await week_fetcher.fetch_activity_data(previous_week=previous_week)
        ids = await get_activity_ids(activities)
        raw_data = await ActivityStreamsFetcher.fetch_multiple_activities_streams(
            api=self.api_async,
            list_id_activities=ids,
            stream_keys=constant.ACTIVITY_STREAMS_KEYS,
        )
        return pd.DataFrame(raw_data)
