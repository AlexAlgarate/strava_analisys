from collections.abc import Iterable, Mapping, Sequence
from contextlib import AbstractContextManager
from typing import Protocol

from src.application.results import ActivityZonesExportResult, StreamExportResult
from src.domain.activity_stream import ActivityStream, StreamBatch
from src.domain.activity_summary import WeeklyActivitySummary
from src.domain.detailed_activity import DetailedActivity
from src.domain.heart_rate_zones import HeartRateZones
from src.presentation.menu.options import MenuOption


class ResultPresenter(Protocol):
    def present_heading(self, heading: str) -> None: ...

    def present_activity_list(
        self,
        activities: Sequence[DetailedActivity],
    ) -> None: ...

    def present_detailed_activities(
        self,
        activities: Sequence[DetailedActivity],
    ) -> None: ...

    def present_activity_stream(self, stream: ActivityStream) -> None: ...

    def present_stream_batch(self, batch: StreamBatch) -> None: ...

    def present_stream_export(self, result: StreamExportResult) -> None: ...

    def present_activity_zones(self, zones: HeartRateZones) -> None: ...

    def present_activity_zones_export(
        self,
        result: ActivityZonesExportResult,
    ) -> None: ...


class ErrorPresenter(Protocol):
    def print_invalid_option(self, option: str) -> None: ...

    def print_operation_error(self, operation: str, error: Exception) -> None: ...


class WeeklySummaryPresenter(Protocol):
    def present_weekly_report(self, summary: WeeklyActivitySummary) -> None: ...


class PromptReader(Protocol):
    def ask_menu_option(self, valid_options: Mapping[str, str]) -> str: ...

    def ask_activity_id(self) -> int: ...

    def ask_activity_ids(self) -> list[int]: ...


class MenuView(Protocol):
    def print_welcome(self) -> None: ...

    def print_menu(self, options: Iterable[MenuOption]) -> None: ...

    def print_goodbye(self) -> None: ...


class OperationProgress(Protocol):
    def track(self, description: str) -> AbstractContextManager[None]: ...
