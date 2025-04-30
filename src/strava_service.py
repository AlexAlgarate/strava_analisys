from typing import Any, Dict, List

import pandas as pd

from src.activities.detailed_activities import (
    DetailedActivitiesFetcher,
    WeeklyActivitiesFetcher,
)
from src.activities.get_streams import ActivityStreamsFetcher
from src.activities.last_200_activities import RecentActivitiesFetcher
from src.activities.one_activity import SingleActivityFetcher
from src.interfaces.strava_api import BaseStravaAPI
from src.interfaces.stream_exporter import StreamExporter
from src.strava_api.api.async_strava_api import AsyncStravaAPI
from src.utils import constants as constant
from src.utils.helpers import get_activity_ids


class CsvExporter(StreamExporter):
    def export(self, df: pd.DataFrame, path: str) -> None:
        df.to_csv(path, index=False)


class StravaService:
    def __init__(
        self,
        api_async: AsyncStravaAPI,
        api_sync: BaseStravaAPI,
        exporter_map: Dict[str, StreamExporter] | None = None,
    ):
        self.api_async = api_async
        self.api_sync = api_sync
        self.exporters = exporter_map or {"csv": CsvExporter()}

    def get_one_activity(self, activity_id: int) -> Dict[str, Any]:
        """Get information for a single activity."""
        return SingleActivityFetcher(
            api=self.api_sync, id_activity=activity_id
        ).fetch_activity_data()

    def get_last_200_activities(self) -> Dict[str, Any]:
        """Get the last 200 activities from Strava."""
        return RecentActivitiesFetcher(self.api_sync).fetch_activity_data()

    async def get_activity_range(self, previous_week: bool = False) -> Dict[str, Any]:
        """Get activities within a specific date range."""
        return await WeeklyActivitiesFetcher(self.api_async).fetch_activity_data(
            previous_week=previous_week
        )

    async def get_activity_details(
        self, previous_week: bool = False
    ) -> List[Dict[Any, Any]]:
        """Get detailed information for activities."""
        keys = [key.value for key in constant.ActivityDetailKey]
        return await DetailedActivitiesFetcher(self.api_async).fetch_activity_data(
            keys=keys, previuos_week=previous_week
        )

    async def get_streams_for_activity(self, activity_id: int) -> Dict[str, Any]:
        """Get detailed stream data for a specific activity."""
        return await ActivityStreamsFetcher(
            api=self.api_async, id_activity=activity_id
        ).fetch_activity_data(stream_keys=constant.ACTIVITY_STREAMS_KEYS)

    async def get_streams_for_multiple_activities(
        self, activity_ids: list[int]
    ) -> Dict[str, Any]:
        """Get detailed stream data for multiple activities."""
        return await ActivityStreamsFetcher.fetch_multiple_activities_streams(
            api=self.api_async,
            list_id_activities=activity_ids,
            stream_keys=constant.ACTIVITY_STREAMS_KEYS,
        )

    async def _get_ids_selected_week(self, previous_week: bool = False) -> List[int]:
        activities = await WeeklyActivitiesFetcher(self.api_async).fetch_activity_data(
            previous_week=previous_week
        )

        activity_ids = await get_activity_ids(activities)
        return activity_ids

    async def _fetch_streams(self, previous_week: bool) -> pd.DataFrame:
        week_fetcher = WeeklyActivitiesFetcher(self.api_async)
        activities = await week_fetcher.fetch_activity_data(previous_week=previous_week)
        ids = await get_activity_ids(activities)
        raw_data = await ActivityStreamsFetcher.fetch_multiple_activities_streams(
            api=self.api_async,
            list_id_activities=ids,
            stream_keys=constant.ACTIVITY_STREAMS_KEYS,
        )
        return pd.DataFrame(raw_data)

    def _create_path(self, output_dir, previous_week, fmt):
        suffix = "previous_week" if previous_week else "current_week"
        filename = f"streams_{suffix}.{fmt}"
        path = f"{output_dir}/{filename}"
        return path

    async def export_streams_for_selected_week(
        self,
        selected_format: str = "csv",
        output_dir: str = ".",
        previous_week: bool = False,
    ) -> pd.DataFrame:
        fmt = selected_format.lower()
        if fmt not in self.exporters:
            raise ValueError(f"Unsupported format: {fmt}")

        df = await self._fetch_streams(previous_week=previous_week)

        path = self._create_path(output_dir, previous_week, fmt)

        exporter = self.exporters[fmt]
        exporter.export(df, path)

        return df
