from collections.abc import Iterable, Mapping
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Protocol

from src.core.service import StreamExportResult
from src.domain.activity_stream import ActivityStream, StreamBatch
from src.domain.activity_summary import WeeklyActivitySummary
from src.domain.detailed_activity import DetailedActivity
from src.domain.heart_rate_zones import HeartRateZones
from src.presentation.menu.options import MenuOption


class StravaUseCases(Protocol):
    async def get_activity_range(
        self,
        previous_week: bool = False,
    ) -> list[DetailedActivity]: ...

    async def get_activity_details(
        self,
        previous_week: bool = False,
    ) -> list[DetailedActivity]: ...

    async def get_streams_for_activity(self, activity_id: int) -> ActivityStream: ...

    async def get_streams_for_multiple_activities(
        self,
        activity_ids: list[int],
    ) -> StreamBatch: ...

    async def export_streams_for_selected_week(
        self,
        selected_format: str = "csv",
        output_dir: str | Path = ".",
        previous_week: bool = False,
    ) -> StreamExportResult: ...

    async def get_activity_zones(
        self,
        activity_id: int,
        save_zones: bool = False,
    ) -> HeartRateZones: ...


class WeeklySummaryUseCase(Protocol):
    async def generate_summary(
        self,
        previous_week: bool = False,
    ) -> WeeklyActivitySummary: ...


class ResultPresenter(Protocol):
    def print_result(self, option: MenuOption, result: object) -> None: ...


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
