from collections.abc import Iterable, Mapping
from contextlib import AbstractContextManager
from typing import Protocol

from src.domain.activity_summary import WeeklyActivitySummary
from src.presentation.menu.options import MenuOption


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
