from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import partial

from src.core.activities.summary.service import ActivitySummaryService
from src.core.service import StravaService
from src.presentation.console_output.console_error_handler import (
    ConsoleErrorHandler,
)
from src.presentation.console_output.result_console_printer import (
    ResultConsolePrinter,
)
from src.presentation.console_output.weekly_summary_presenter import (
    ConsoleSummaryPresenter,
)
from src.presentation.menu.options import MenuOption
from src.utils import constants as constant

type MenuAction = Callable[[], Awaitable[object]]


@dataclass(frozen=True, slots=True)
class MenuDependencies:
    service: StravaService
    result_printer: ResultConsolePrinter
    error_printer: ConsoleErrorHandler
    summary_service: ActivitySummaryService | None
    summary_presenter: ConsoleSummaryPresenter


class MenuHandler:
    def __init__(
        self,
        service: StravaService,
        result_console_printer: ResultConsolePrinter | None = None,
        error_console_printer: ConsoleErrorHandler | None = None,
        summary_service: ActivitySummaryService | None = None,
        summary_presenter: ConsoleSummaryPresenter | None = None,
    ) -> None:
        self.dependencies = MenuDependencies(
            service=service,
            result_printer=result_console_printer or ResultConsolePrinter(),
            error_printer=error_console_printer or ConsoleErrorHandler(),
            summary_service=summary_service,
            summary_presenter=summary_presenter or ConsoleSummaryPresenter(),
        )
        self._init_menu_options()

    def _init_menu_options(self) -> None:
        self._menu_options: dict[MenuOption, MenuAction] = {
            MenuOption.ACTIVITY_DETAILS: partial(
                self.dependencies.service.get_activity_details,
                previous_week=False,
            ),
            MenuOption.ACTIVITY_DETAILS_PREV_WEEK: partial(
                self.dependencies.service.get_activity_details,
                previous_week=True,
            ),
            MenuOption.ACTIVITY_RANGE: partial(
                self.dependencies.service.get_activity_range,
                previous_week=False,
            ),
            MenuOption.ACTIVITY_RANGE_PREV_WEEK: partial(
                self.dependencies.service.get_activity_range,
                previous_week=True,
            ),
            MenuOption.SINGLE_STREAM: self._handle_single_stream,
            MenuOption.MULTIPLE_STREAMS: self._handle_multiple_streams,
            MenuOption.STREAMS_CURRENT_WEEK: partial(
                self.dependencies.service.export_streams_for_selected_week,
                previous_week=False,
            ),
            MenuOption.STREAMS_PREV_WEEK: partial(
                self.dependencies.service.export_streams_for_selected_week,
                previous_week=True,
            ),
            MenuOption.WEEKLY_REPORT: self._generate_weekly_report,
        }

    async def _handle_single_stream(self) -> object:
        return await self.dependencies.service.get_streams_for_activity(
            activity_id=constant.EXAMPLE_ID_ONE_ACTIVITY
        )

    async def _handle_multiple_streams(self) -> object:
        return await self.dependencies.service.get_streams_for_multiple_activities(
            activity_ids=constant.EXAMPLE_ID_ACTIVITIES
        )

    async def _generate_weekly_report(self) -> None:
        if self.dependencies.summary_service is None:
            raise RuntimeError("No weekly summary service has been configured.")
        summary = await self.dependencies.summary_service.generate_summary()
        self.dependencies.summary_presenter.present_weekly_report(summary)

    def get_menu_options(self) -> dict[str, str]:
        return {str(option.id): option.description for option in MenuOption}

    async def execute_option(self, option: str) -> object:
        try:
            menu_option = self._validate_option(option=option)
            result = await self._menu_options[menu_option]()
            if result is not None:
                self.dependencies.result_printer.print_result(
                    option=option,
                    result=result,
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
