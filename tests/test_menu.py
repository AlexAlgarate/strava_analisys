import logging
from contextlib import nullcontext
from dataclasses import dataclass
from io import StringIO
from unittest.mock import AsyncMock, Mock

import pytest
from rich.console import Console

from src.application.use_cases.activity_summary import ActivitySummaryService
from src.domain.activity_stream import StreamBatch
from src.domain.activity_summary import WeeklyActivitySummary
from src.presentation.cli_entrypoint import MenuDependencies, MenuHandler
from src.presentation.console_output.console import STRAVA_THEME
from src.presentation.console_output.console_error_handler import (
    ConsoleErrorHandler,
)
from src.presentation.console_output.prompts import ConsolePrompts
from src.presentation.console_output.result_console_printer import (
    ResultConsolePrinter,
)
from src.presentation.console_output.weekly_summary_presenter import (
    ConsoleSummaryPresenter,
)
from src.presentation.menu.options import MenuOption
from src.presentation.menu.renderer import MenuRenderer
from tests.factories import activity_model


@pytest.fixture
def output() -> StringIO:
    return StringIO()


@pytest.fixture
def console(output: StringIO) -> Console:
    return Console(
        file=output,
        theme=STRAVA_THEME,
        color_system=None,
        width=120,
    )


@dataclass(frozen=True, slots=True)
class UseCaseMocks:
    activities: Mock
    streams: Mock
    stream_export: Mock
    activity_zones: Mock


@pytest.fixture
def use_cases() -> UseCaseMocks:
    activities = Mock()
    activities.get_activity_details = AsyncMock()
    activities.get_activity_range = AsyncMock()
    streams = Mock()
    streams.get_streams_for_activity = AsyncMock()
    streams.get_streams_for_multiple_activities = AsyncMock()
    stream_export = Mock()
    stream_export.export_streams_for_selected_week = AsyncMock()
    activity_zones = Mock()
    activity_zones.get_activity_zones = AsyncMock()
    return UseCaseMocks(
        activities=activities,
        streams=streams,
        stream_export=stream_export,
        activity_zones=activity_zones,
    )


@pytest.fixture
def mock_result_printer() -> Mock:
    return Mock(spec=ResultConsolePrinter)


@pytest.fixture
def mock_error_printer() -> Mock:
    return Mock(spec=ConsoleErrorHandler)


@pytest.fixture
def mock_prompts() -> Mock:
    prompts = Mock(spec=ConsolePrompts)
    prompts.ask_activity_id.return_value = 123
    prompts.ask_activity_ids.return_value = [123, 456]
    prompts.ask_menu_option.return_value = "1"
    return prompts


@pytest.fixture
def mock_menu_view() -> Mock:
    return Mock(spec=MenuRenderer)


@pytest.fixture
def mock_progress() -> Mock:
    progress = Mock()
    progress.track.return_value = nullcontext()
    return progress


@pytest.fixture
def menu_handler(
    use_cases: UseCaseMocks,
    mock_result_printer: Mock,
    mock_error_printer: Mock,
    mock_prompts: Mock,
    mock_menu_view: Mock,
    mock_progress: Mock,
) -> MenuHandler:
    return MenuHandler(
        MenuDependencies(
            activities=use_cases.activities,
            streams=use_cases.streams,
            stream_export=use_cases.stream_export,
            activity_zones=use_cases.activity_zones,
            summary=None,
            result_printer=mock_result_printer,
            error_printer=mock_error_printer,
            summary_presenter=Mock(spec=ConsoleSummaryPresenter),
            prompts=mock_prompts,
            menu_view=mock_menu_view,
            progress=mock_progress,
        )
    )


class TestMenuHandler:
    def test_keeps_injected_dependencies(
        self,
        menu_handler: MenuHandler,
        use_cases: UseCaseMocks,
        mock_prompts: Mock,
    ) -> None:
        assert isinstance(menu_handler.dependencies, MenuDependencies)
        assert menu_handler.dependencies.activities is use_cases.activities
        assert menu_handler.dependencies.streams is use_cases.streams
        assert menu_handler.dependencies.stream_export is use_cases.stream_export
        assert menu_handler.dependencies.activity_zones is use_cases.activity_zones
        assert menu_handler.dependencies.prompts is mock_prompts

    def test_get_menu_options(self, menu_handler: MenuHandler) -> None:
        options = menu_handler.get_menu_options()

        assert len(options) == len(MenuOption)
        assert options["10"] == "View heart-rate zones"

    def test_asks_for_a_valid_menu_option(
        self,
        menu_handler: MenuHandler,
        mock_prompts: Mock,
    ) -> None:
        assert menu_handler.ask_option() == "1"
        mock_prompts.ask_menu_option.assert_called_once_with(
            menu_handler.get_menu_options()
        )

    @pytest.mark.asyncio
    async def test_execute_invalid_option(
        self,
        menu_handler: MenuHandler,
        mock_error_printer: Mock,
    ) -> None:
        result = await menu_handler.execute_option("999")

        assert result is None
        mock_error_printer.print_invalid_option.assert_called_once_with("999")

    @pytest.mark.parametrize(
        ("option", "use_case", "service_method", "previous_week"),
        [
            (
                MenuOption.ACTIVITY_DETAILS,
                "activities",
                "get_activity_details",
                False,
            ),
            (
                MenuOption.ACTIVITY_DETAILS_PREV_WEEK,
                "activities",
                "get_activity_details",
                True,
            ),
            (MenuOption.ACTIVITY_RANGE, "activities", "get_activity_range", False),
            (
                MenuOption.ACTIVITY_RANGE_PREV_WEEK,
                "activities",
                "get_activity_range",
                True,
            ),
            (
                MenuOption.STREAMS_CURRENT_WEEK,
                "stream_export",
                "export_streams_for_selected_week",
                False,
            ),
            (
                MenuOption.STREAMS_PREV_WEEK,
                "stream_export",
                "export_streams_for_selected_week",
                True,
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_executes_period_options(
        self,
        menu_handler: MenuHandler,
        use_cases: UseCaseMocks,
        mock_result_printer: Mock,
        option: MenuOption,
        use_case: str,
        service_method: str,
        previous_week: bool,
    ) -> None:
        method = getattr(getattr(use_cases, use_case), service_method)
        method.return_value = [activity_model()]

        result = await menu_handler.execute_option(str(option.id))

        assert result == method.return_value
        method.assert_awaited_once_with(previous_week=previous_week)
        mock_result_printer.print_result.assert_called_once_with(
            option=option,
            result=method.return_value,
        )

    @pytest.mark.parametrize(
        ("option", "use_case", "service_method", "expected_argument"),
        [
            (
                MenuOption.SINGLE_STREAM,
                "streams",
                "get_streams_for_activity",
                123,
            ),
            (
                MenuOption.MULTIPLE_STREAMS,
                "streams",
                "get_streams_for_multiple_activities",
                [123, 456],
            ),
            (
                MenuOption.ACTIVITY_ZONES,
                "activity_zones",
                "get_activity_zones",
                123,
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_stream_and_zone_options_use_prompted_ids(
        self,
        menu_handler: MenuHandler,
        use_cases: UseCaseMocks,
        option: MenuOption,
        use_case: str,
        service_method: str,
        expected_argument: object,
    ) -> None:
        method = getattr(getattr(use_cases, use_case), service_method)
        method.return_value = StreamBatch()

        await menu_handler.execute_option(str(option.id))

        method.assert_awaited_once_with(expected_argument)

    @pytest.mark.asyncio
    async def test_operation_errors_are_not_reported_as_invalid_options(
        self,
        menu_handler: MenuHandler,
        use_cases: UseCaseMocks,
        mock_error_printer: Mock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        error = RuntimeError("Strava is unavailable")
        use_cases.activities.get_activity_details.side_effect = error

        with caplog.at_level(logging.ERROR, logger="src.presentation.cli_entrypoint"):
            result = await menu_handler.execute_option(
                str(MenuOption.ACTIVITY_DETAILS.id)
            )

        assert result is None
        assert "Menu operation failed" in caplog.text
        assert caplog.records[-1].exc_info is not None
        mock_error_printer.print_operation_error.assert_called_once_with(
            MenuOption.ACTIVITY_DETAILS.description,
            error,
        )
        mock_error_printer.print_invalid_option.assert_not_called()

    @pytest.mark.asyncio
    async def test_weekly_report_requires_summary_service(
        self,
        menu_handler: MenuHandler,
        mock_error_printer: Mock,
    ) -> None:
        await menu_handler.execute_option(str(MenuOption.WEEKLY_REPORT.id))

        mock_error_printer.print_operation_error.assert_called_once()

    @pytest.mark.asyncio
    async def test_weekly_report_uses_live_summary_service(
        self,
        use_cases: UseCaseMocks,
        mock_result_printer: Mock,
        mock_error_printer: Mock,
        mock_prompts: Mock,
        mock_menu_view: Mock,
        mock_progress: Mock,
    ) -> None:
        summary = WeeklyActivitySummary.from_activities([])
        summary_service = Mock(spec=ActivitySummaryService)
        summary_service.generate_summary = AsyncMock(return_value=summary)
        presenter = Mock(spec=ConsoleSummaryPresenter)
        handler = MenuHandler(
            MenuDependencies(
                activities=use_cases.activities,
                streams=use_cases.streams,
                stream_export=use_cases.stream_export,
                activity_zones=use_cases.activity_zones,
                summary=summary_service,
                result_printer=mock_result_printer,
                error_printer=mock_error_printer,
                summary_presenter=presenter,
                prompts=mock_prompts,
                menu_view=mock_menu_view,
                progress=mock_progress,
            )
        )

        result = await handler.execute_option(str(MenuOption.WEEKLY_REPORT.id))

        assert result is None
        summary_service.generate_summary.assert_awaited_once_with()
        presenter.present_weekly_report.assert_called_once_with(summary)
        mock_result_printer.print_result.assert_not_called()

    def test_renders_welcome_menu_and_goodbye(
        self,
        menu_handler: MenuHandler,
        mock_menu_view: Mock,
    ) -> None:
        menu_handler.print_welcome()
        menu_handler.print_menu()
        menu_handler.print_goodbye()

        mock_menu_view.print_welcome.assert_called_once_with()
        mock_menu_view.print_menu.assert_called_once_with(MenuOption)
        mock_menu_view.print_goodbye.assert_called_once_with()

    def test_validate_option(self, menu_handler: MenuHandler) -> None:
        assert menu_handler._validate_option("1") is MenuOption.ACTIVITY_DETAILS
        with pytest.raises(ValueError, match="Option 999 not found"):
            menu_handler._validate_option("999")
