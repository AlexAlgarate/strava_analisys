from collections.abc import Mapping
from pathlib import Path

from src.core.activities.service import ActivityService
from src.core.activities.zones import ActivityZones
from src.core.concurrency import DEFAULT_MAX_CONCURRENCY
from src.core.ports.export import (
    ActivityZonesWriter,
    StreamExporter,
)
from src.core.ports.strava import StravaAPI
from src.core.streams.exporter import DataExporter
from src.core.streams.manager import StreamManager
from src.domain.activity_stream import ActivityStream, StreamBatch
from src.domain.detailed_activity import DetailedActivity
from src.domain.heart_rate_zones import HeartRateZones


class StravaService:
    """Application facade for activity and stream use cases."""

    def __init__(
        self,
        api: StravaAPI,
        exporters: Mapping[str, StreamExporter] | None = None,
        zones_writer: ActivityZonesWriter | None = None,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    ) -> None:
        self._api = api
        self._activity_service = ActivityService(
            api,
            max_concurrency=max_concurrency,
        )
        self._stream_manager = StreamManager(
            api,
            max_concurrency=max_concurrency,
        )
        self._data_exporter = DataExporter(exporters or {})
        self._zones_writer = zones_writer

    async def get_activity_range(
        self, previous_week: bool = False
    ) -> list[DetailedActivity]:
        return await self._activity_service.get_activity_range(previous_week)

    async def get_activity_details(
        self, previous_week: bool = False
    ) -> list[DetailedActivity]:
        return await self._activity_service.get_activity_details(previous_week)

    async def get_streams_for_activity(self, activity_id: int) -> ActivityStream:
        return await self._stream_manager.get_streams_for_activity(activity_id)

    async def get_streams_for_multiple_activities(
        self, activity_ids: list[int]
    ) -> StreamBatch:
        return await self._stream_manager.get_streams_for_multiple_activities(
            activity_ids
        )

    async def export_streams_for_selected_week(
        self,
        selected_format: str = "csv",
        output_dir: str | Path = ".",
        previous_week: bool = False,
    ) -> StreamBatch:
        batch = await self._stream_manager.get_weekly_streams(
            previous_week=previous_week
        )
        self._data_exporter.export_streams(
            batch.streams,
            selected_format=selected_format,
            output_dir=output_dir,
            previous_week=previous_week,
        )
        return batch

    async def get_activity_zones(
        self, activity_id: int, save_zones: bool = False
    ) -> HeartRateZones:
        zones = ActivityZones(
            api=self._api,
            activity_id=activity_id,
            writer=self._zones_writer,
        )
        return await zones.get_zones(save_zones=save_zones)
