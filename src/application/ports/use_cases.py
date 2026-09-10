from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from src.application.results import ActivityZonesExportResult, StreamExportResult
from src.domain.activity_stream import ActivityStream, StreamBatch
from src.domain.activity_summary import WeeklyActivitySummary
from src.domain.detailed_activity import DetailedActivity
from src.domain.heart_rate_zones import HeartRateZones
from src.domain.week_period import WeekSelection


class ActivityQueries(Protocol):
    """Queries that expose weekly activity data."""

    async def get_activity_range(
        self,
        *,
        week: WeekSelection,
    ) -> list[DetailedActivity]: ...

    async def get_activity_details(
        self,
        *,
        week: WeekSelection,
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
        *,
        week: WeekSelection,
    ) -> StreamBatch: ...


class StreamExportUseCase(Protocol):
    """Export all streams for a selected week."""

    async def export_streams_for_selected_week(
        self,
        selected_format: str = "csv",
        output_dir: str | Path = ".",
        *,
        week: WeekSelection,
    ) -> StreamExportResult: ...


class ActivityZonesUseCase(Protocol):
    """Retrieve heart-rate zones for one activity."""

    async def get_activity_zones(
        self,
        activity_id: int,
    ) -> HeartRateZones: ...


class ActivityZonesExportUseCase(Protocol):
    """Retrieve and persist heart-rate zones for one activity."""

    async def export_activity_zones(
        self,
        activity_id: int,
    ) -> ActivityZonesExportResult: ...


class WeeklySummaryUseCase(Protocol):
    """Build aggregate metrics for a selected week."""

    async def generate_summary(
        self,
        *,
        week: WeekSelection,
    ) -> WeeklyActivitySummary: ...
