from collections.abc import Mapping
from pathlib import Path

import pandas as pd

from src.core.activities.fetchers import ActivityData
from src.core.activities.service import ActivityService
from src.core.activities.zones import ActivityZones
from src.core.ports.export import (
    ActivityDetailsWriter,
    ActivityZonesWriter,
    StreamExporter,
)
from src.core.ports.strava import StravaAPI
from src.core.streams.exporter import DataExporter
from src.core.streams.manager import StreamManager


class StravaService:
    """Application facade for activity and stream use cases."""

    def __init__(
        self,
        api: StravaAPI,
        exporters: Mapping[str, StreamExporter] | None = None,
        details_writer: ActivityDetailsWriter | None = None,
        zones_writer: ActivityZonesWriter | None = None,
    ) -> None:
        self._api = api
        self._activity_service = ActivityService(api, details_writer)
        self._stream_manager = StreamManager(api)
        self._data_exporter = DataExporter(exporters or {})
        self._zones_writer = zones_writer

    async def get_activity_range(
        self, previous_week: bool = False
    ) -> list[ActivityData]:
        return await self._activity_service.get_activity_range(previous_week)

    async def get_activity_details(
        self, previous_week: bool = False
    ) -> list[ActivityData]:
        return await self._activity_service.get_activity_details(previous_week)

    async def get_streams_for_activity(self, activity_id: int) -> pd.DataFrame:
        return await self._stream_manager.get_streams_for_activity(activity_id)

    async def get_streams_for_multiple_activities(
        self, activity_ids: list[int]
    ) -> pd.DataFrame:
        return await self._stream_manager.get_streams_for_multiple_activities(
            activity_ids
        )

    async def export_streams_for_selected_week(
        self,
        selected_format: str = "csv",
        output_dir: str | Path = ".",
        previous_week: bool = False,
    ) -> pd.DataFrame:
        data = await self._stream_manager.get_weekly_streams(
            previous_week=previous_week
        )
        self._data_exporter.export_streams(
            data,
            selected_format=selected_format,
            output_dir=output_dir,
            previous_week=previous_week,
        )
        return data

    async def get_activity_zones(
        self, activity_id: int, save_zones: bool = False
    ) -> dict[str, object]:
        zones = ActivityZones(
            api=self._api,
            activity_id=activity_id,
            writer=self._zones_writer,
        )
        return await zones.get_zones(save_zones=save_zones)
