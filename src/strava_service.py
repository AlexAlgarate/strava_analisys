from typing import Any, Dict, List

import pandas as pd

from src.core.activities.service import ActivityService
from src.core.activities.zones import ActivityZones
from src.core.streams.exporter import DataExporter
from src.core.streams.manager import StreamManager
from src.infrastructure.api_clients.async_strava_api import AsyncStravaAPI
from src.interfaces.stream_exporter import IStreamExporter


class StravaService:
    def __init__(
        self,
        api_async: AsyncStravaAPI,
        exporter_map: Dict[str, IStreamExporter] | None = None,
    ):
        self.api_async = api_async
        self.activity_manager = ActivityService(api_async)
        self.stream_manager = StreamManager(api_async)
        self.data_exporter = DataExporter(exporter_map)

    async def get_activity_range(self, previous_week: bool = False) -> Any:
        """Get activity data for a specific date range."""
        return await self.activity_manager.get_activity_range(previous_week)

    async def get_activity_details(
        self, previous_week: bool = False
    ) -> List[Dict[Any, Any]]:
        """Get detailed activity information."""
        return await self.activity_manager.get_activity_details(previous_week)

    async def get_streams_for_activity(self, activity_id: int) -> pd.DataFrame:
        """Get stream data for a specific activity."""
        return await self.stream_manager.get_streams_for_activity(activity_id)

    async def get_streams_for_multiple_activities(
        self, activity_ids: list[int]
    ) -> pd.DataFrame:
        """Get stream data for multiple activities."""
        return await self.stream_manager.get_streams_for_multiple_activities(
            activity_ids
        )

    async def export_streams_for_selected_week(
        self,
        selected_format: str = "csv",
        output_dir: str = ".",
        previous_week: bool = False,
    ) -> pd.DataFrame:
        """Export stream data for activities in the selected week."""
        df = await self.stream_manager.get_weekly_streams(
            previous_week=previous_week
        )
        self.data_exporter.export_streams(
            df,
            selected_format=selected_format,
            output_dir=output_dir,
            previous_week=previous_week,
        )
        return df

    async def get_activity_zones(
        self, activity_id: int, save_zones: bool = False
    ) -> Dict[str, int]:
        """Get heart rate zones for a specific activity."""
        zones_manager = ActivityZones(
            api=self.api_async, id_activity=activity_id
        )
        return await zones_manager.get_zones(save_zones=save_zones)
