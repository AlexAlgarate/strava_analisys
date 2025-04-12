import asyncio
from typing import Any, Callable, Dict

from src.menu.console_error_handler import ConsoleErrorHandler
from src.menu.options import MenuOption
from src.menu.result_console_printer import ResultConsolePrinter
from src.strava_service import StravaService
from src.utils import constants as constant


class MenuHandler:
    def __init__(
        self,
        service: StravaService,
        result_console_printer: ResultConsolePrinter = None,
        error_console_printer: ConsoleErrorHandler = None,
    ) -> None:
        self.service = service
        self.result_console_printer = result_console_printer
        self.error_console_printer = error_console_printer

        self.menu_options: Dict[MenuOption, Callable[[], Any]] = {
            MenuOption.ONE_ACTIVITY: lambda: self.service.get_one_activity(
                activity_id=13654451097
            ),
            MenuOption.LAST_200_ACTIVITIES: self.service.get_last_200_activities,
            MenuOption.ACTIVITY_DETAILS: lambda: self._handle_async(
                self.service.get_activity_details, False
            ),
            MenuOption.ACTIVITY_DETAILS_PREV_WEEK: lambda: self._handle_async(
                self.service.get_activity_details, True
            ),
            MenuOption.ACTIVITY_RANGE: lambda: self._handle_async(
                self.service.get_activity_range, False
            ),
            MenuOption.ACTIVITY_RANGE_PREV_WEEK: lambda: self._handle_async(
                self.service.get_activity_range, True
            ),
            MenuOption.SINGLE_STREAM: lambda: self._handle_single_stream(),
            MenuOption.MULTIPLE_STREAMS: lambda: self._handle_multiple_streams(),
        }

    def _handle_async(self, func: Callable, previous_week: bool) -> Any:
        return asyncio.run(func(previous_week=previous_week))

    def _handle_single_stream(self) -> Any:
        return asyncio.run(
            self.service.get_streams_for_activity(
                activity_id=constant.EXAMPLE_ID_ONE_ACTIVITY
            )
        )

    def _handle_multiple_streams(self) -> Any:
        return asyncio.run(
            self.service.get_streams_for_multiple_activities(
                activity_ids=constant.EXAMPLE_ID_ACTIVITIES
            )
        )

    def get_menu_options(self, menu_option: MenuOption) -> Dict[str, str]:
        return {str(option.id): option.description for option in menu_option}

    def execute_option(self, option: str) -> Any:
        try:
            menu_option = self._validate_option(option=option)

            result = self.menu_options[menu_option]()

            self.result_console_printer.print_result(option=option, result=result)
            return result
        except (ValueError, KeyError):
            self.error_console_printer.print_error(option=option)
            return None

    def _validate_option(self, option: str) -> MenuOption:
        valid_options = {str(opt.id): opt for opt in MenuOption}
        if option not in valid_options:
            raise ValueError(f"Option {option} not found")

        return valid_options[option]

    def print_menu(self, menu_option: MenuOption) -> None:
        print("\n📌 Choose an option: \n")
        for key, desc in self.get_menu_options(menu_option=menu_option).items():
            print(f"{key}. {desc}")
