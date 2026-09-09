from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from src.application.results import StreamExportResult
from src.domain.activity_stream import ActivityStream, StreamBatch
from src.domain.activity_summary import WeeklyActivitySummary
from src.domain.detailed_activity import DetailedActivity
from src.domain.heart_rate_zones import HeartRateZones


class ActivityQueries(Protocol):
    """Queries that expose weekly activity data."""

    async def get_activity_range(
        self,
        previous_week: bool = False,
    ) -> list[DetailedActivity]: ...

    async def get_activity_details(
        self,
        previous_week: bool = False,
    ) -> list[DetailedActivity]: ...


class ActivityStreamQueries(Protocol):
    """Queries that expose activity streams."""

    async def get_streams_for_activity(self, activity_id: int) -> ActivityStream: ...

    async def get_streams_for_multiple_activities(
        self,
        activity_ids: Sequence[int],
    ) -> StreamBatch: ...

    async def get_weekly_streams(
        self,
        previous_week: bool = False,
    ) -> StreamBatch: ...


class StreamExportUseCase(Protocol):
    """Export all streams for a selected week."""

    async def export_streams_for_selected_week(
        self,
        selected_format: str = "csv",
        output_dir: str | Path = ".",
        previous_week: bool = False,
    ) -> StreamExportResult: ...


class ActivityZonesUseCase(Protocol):
    """Retrieve and optionally persist heart-rate zones."""

    async def get_activity_zones(
        self,
        activity_id: int,
        save_zones: bool = False,
    ) -> HeartRateZones: ...


class WeeklySummaryUseCase(Protocol):
    """Build aggregate metrics for a selected week."""

    async def generate_summary(
        self,
        previous_week: bool = False,
    ) -> WeeklyActivitySummary: ...
