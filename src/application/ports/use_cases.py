from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from src.application.results import ActivityZonesExportResult, StreamExportResult
from src.domain.activity_stream import ActivityStream, StreamBatch
from src.domain.activity_summary import WeeklyActivitySummary
from src.domain.detailed_activity import DetailedActivity
from src.domain.heart_rate_zones import HeartRateZones
from src.domain.week_period import WeekSelection


class WeeklyActivityList(Protocol):
    """List activities for a selected week."""

    async def list_activities(
        self,
        *,
        week: WeekSelection,
    ) -> list[DetailedActivity]: ...


class WeeklyDetailedActivityList(Protocol):
    """List full activity details for a selected week."""

    async def list_detailed_activities(
        self,
        *,
        week: WeekSelection,
    ) -> list[DetailedActivity]: ...


class WeeklyActivityQueries(
    WeeklyActivityList,
    WeeklyDetailedActivityList,
    Protocol,
):
    """Expose both compact and detailed weekly activity queries."""


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


class WeeklyStreamBatchProvider(Protocol):
    """Load the activity-stream batch for a selected week."""

    async def get_weekly_streams(
        self,
        *,
        week: WeekSelection,
    ) -> StreamBatch: ...


class StreamExportUseCase(Protocol):
    """Export all streams for a selected week."""

    @property
    def supported_formats(self) -> tuple[str, ...]: ...

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
