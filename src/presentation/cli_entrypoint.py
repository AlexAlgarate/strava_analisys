import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.presentation.console_output.console_error_handler import (
    ConsoleErrorHandler,
)
from src.presentation.console_output.result_console_printer import (
    ResultConsolePrinter,
)
from src.presentation.menu.options import MenuOption
from src.strava_service import StravaService
from src.utils import constants as constant


@dataclass
class MenuDependencies:
    service: StravaService
    result_printer: ResultConsolePrinter
    error_printer: ConsoleErrorHandler


class MenuHandler:
    def __init__(
        self,
        service: StravaService,
        result_console_printer: Optional[ResultConsolePrinter] = None,
        error_console_printer: Optional[ConsoleErrorHandler] = None,
    ) -> None:
        self.dependencies = MenuDependencies(
            service=service,
            result_printer=result_console_printer or ResultConsolePrinter(),
            error_printer=error_console_printer or ConsoleErrorHandler(),
        )
        self._init_menu_options()

    def _init_menu_options(self) -> None:
        self.menu_options: Dict[MenuOption, Callable[[], Any]] = {
            MenuOption.ACTIVITY_DETAILS: lambda: self._handle_async(
                self.dependencies.service.get_activity_details, False
            ),
            MenuOption.ACTIVITY_DETAILS_PREV_WEEK: lambda: self._handle_async(
                self.dependencies.service.get_activity_details, True
            ),
            MenuOption.ACTIVITY_RANGE: lambda: self._handle_async(
                self.dependencies.service.get_activity_range, False
            ),
            MenuOption.ACTIVITY_RANGE_PREV_WEEK: lambda: self._handle_async(
                self.dependencies.service.get_activity_range, True
            ),
            MenuOption.SINGLE_STREAM: self._handle_single_stream,
            MenuOption.MULTIPLE_STREAMS: self._handle_multiple_streams,
            MenuOption.STREAMS_CURRENT_WEEK: lambda: self._handle_async(
                self.dependencies.service.export_streams_for_selected_week,
                False,
            ),
            MenuOption.STREAMS_PREV_WEEK: lambda: self._handle_async(
                self.dependencies.service.export_streams_for_selected_week, True
            ),
        }

    def _provisional_handle_feature(self) -> Any:
        return "This feature is not yet implemented."

    def _handle_async(
        self, func: Callable, previous_week: bool | None = None
    ) -> Any:
        return asyncio.run(func(previous_week=previous_week))

    def _handle_single_stream(self) -> Any:
        return asyncio.run(
            self.dependencies.service.get_streams_for_activity(
                activity_id=constant.EXAMPLE_ID_ONE_ACTIVITY
            )
        )

    def _handle_weekly_streams(self, previous_week: bool) -> Any:
        return asyncio.run(
            self.dependencies.service.export_streams_for_selected_week(
                previous_week=previous_week
            )
        )

    def _handle_multiple_streams(self) -> Any:
        return asyncio.run(
            self.dependencies.service.get_streams_for_multiple_activities(
                activity_ids=constant.EXAMPLE_ID_ACTIVITIES
            )
        )

    def get_menu_options(self) -> Dict[str, str]:
        return {str(option.id): option.description for option in MenuOption}

    def execute_option(self, option: str) -> Optional[Any]:
        try:
            menu_option = self._validate_option(option=option)
            result = self.menu_options[menu_option]()
            self.dependencies.result_printer.print_result(
                option=option, result=result
            )
            return result
        except (ValueError, KeyError):
            self.dependencies.error_printer.print_error(option=option)
            return None

    def _validate_option(self, option: str) -> MenuOption:
        valid_options = {str(opt.id): opt for opt in MenuOption}
        if option not in valid_options:
            raise ValueError(f"Option {option} not found")
        return valid_options[option]

    def print_menu(self) -> None:
        print("\n📌 Choose an option: \n")
        for key, desc in self.get_menu_options().items():
            print(f"{key}. {desc}")
