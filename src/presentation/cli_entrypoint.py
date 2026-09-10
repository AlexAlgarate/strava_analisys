from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from functools import partial

from src.application.ports.use_cases import (
    ActivityQueries,
    ActivityStreamQueries,
    ActivityZonesUseCase,
    StreamExportUseCase,
    WeeklySummaryUseCase,
)
from src.presentation.menu.options import MenuOption
from src.presentation.ports import (
    ErrorPresenter,
    MenuView,
    OperationProgress,
    PromptReader,
    ResultPresenter,
    WeeklySummaryPresenter,
)

type MenuAction = Callable[[], Awaitable[object]]


@dataclass(frozen=True, slots=True)
class MenuDependencies:
    activities: ActivityQueries
    streams: ActivityStreamQueries
    stream_export: StreamExportUseCase
    activity_zones: ActivityZonesUseCase
    summary: WeeklySummaryUseCase | None
    result_printer: ResultPresenter
    error_printer: ErrorPresenter
    summary_presenter: WeeklySummaryPresenter
    prompts: PromptReader
    menu_view: MenuView
    progress: OperationProgress


class MenuHandler:
    def __init__(self, dependencies: MenuDependencies) -> None:
        self.dependencies = dependencies
        self._init_menu_options()

    def _init_menu_options(self) -> None:
        self._menu_options: dict[MenuOption, MenuAction] = {
            MenuOption.ACTIVITY_DETAILS: partial(
                self.dependencies.activities.get_activity_details,
                previous_week=False,
            ),
            MenuOption.ACTIVITY_DETAILS_PREV_WEEK: partial(
                self.dependencies.activities.get_activity_details,
                previous_week=True,
            ),
            MenuOption.ACTIVITY_RANGE: partial(
                self.dependencies.activities.get_activity_range,
                previous_week=False,
            ),
            MenuOption.ACTIVITY_RANGE_PREV_WEEK: partial(
                self.dependencies.activities.get_activity_range,
                previous_week=True,
            ),
            MenuOption.SINGLE_STREAM: self._handle_single_stream,
            MenuOption.MULTIPLE_STREAMS: self._handle_multiple_streams,
            MenuOption.STREAMS_CURRENT_WEEK: partial(
                self.dependencies.stream_export.export_streams_for_selected_week,
                previous_week=False,
            ),
            MenuOption.STREAMS_PREV_WEEK: partial(
                self.dependencies.stream_export.export_streams_for_selected_week,
                previous_week=True,
            ),
            MenuOption.WEEKLY_REPORT: self._generate_weekly_report,
            MenuOption.ACTIVITY_ZONES: self._handle_activity_zones,
        }

    async def _handle_single_stream(self) -> object:
        activity_id = self.dependencies.prompts.ask_activity_id()
        return await self.dependencies.streams.get_streams_for_activity(activity_id)

    async def _handle_multiple_streams(self) -> object:
        activity_ids = self.dependencies.prompts.ask_activity_ids()
        return await self.dependencies.streams.get_streams_for_multiple_activities(
            activity_ids
        )

    async def _handle_activity_zones(self) -> object:
        activity_id = self.dependencies.prompts.ask_activity_id()
        return await self.dependencies.activity_zones.get_activity_zones(activity_id)

    async def _generate_weekly_report(self) -> None:
        if self.dependencies.summary is None:
            raise RuntimeError("No weekly summary service has been configured.")
        summary = await self.dependencies.summary.generate_summary()
        self.dependencies.summary_presenter.present_weekly_report(summary)

    def get_menu_options(self) -> dict[str, str]:
        return {str(option.id): option.description for option in MenuOption}

    def ask_option(self) -> str:
        return self.dependencies.prompts.ask_menu_option(self.get_menu_options())

    async def execute_option(self, option: str) -> object | None:
        try:
            menu_option = self._validate_option(option=option)
        except ValueError:
            self.dependencies.error_printer.print_invalid_option(option)
            return None

        try:
            with self.dependencies.progress.track(menu_option.description):
                result = await self._menu_options[menu_option]()
        except Exception as error:  # noqa: BLE001 - terminal boundary stays alive
            self.dependencies.error_printer.print_operation_error(
                menu_option.description,
                error,
            )
            return None

        if result is not None:
            self.dependencies.result_printer.print_result(
                option=menu_option,
                result=result,
            )
        return result

    def _validate_option(self, option: str) -> MenuOption:
        valid_options = {str(item.id): item for item in MenuOption}
        try:
            return valid_options[option]
        except KeyError as error:
            raise ValueError(f"Option {option} not found") from error

    def print_welcome(self) -> None:
        self.dependencies.menu_view.print_welcome()

    def print_menu(self) -> None:
        self.dependencies.menu_view.print_menu(MenuOption)

    def print_goodbye(self) -> None:
        self.dependencies.menu_view.print_goodbye()
