from unittest.mock import AsyncMock, Mock

import pandas as pd
import pytest

from src.core.activities.summary.service import ActivitySummaryService
from src.domain.activity_summary import WeeklyActivitySummary
from src.domain.detailed_activity import DetailedActivity
from src.presentation.cli_entrypoint import MenuDependencies, MenuHandler
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
from tests.factories import activity_payload


@pytest.fixture
def mock_service() -> Mock:
    service = Mock()
    service.get_one_activity = Mock()
    service.get_last_200_activities = Mock()
    service.get_activity_details = AsyncMock()
    service.get_activity_range = AsyncMock()
    service.get_streams_for_activity = AsyncMock()
    service.get_streams_for_multiple_activities = AsyncMock()
    return service


@pytest.fixture
def mock_result_printer() -> Mock:
    printer = Mock(spec=ResultConsolePrinter)
    printer.print_result = Mock()
    return printer


@pytest.fixture
def mock_error_printer() -> Mock:
    printer = Mock(spec=ConsoleErrorHandler)
    printer.print_error = Mock()
    return printer


@pytest.fixture
def menu_handler(
    mock_service: Mock, mock_result_printer: Mock, mock_error_printer: Mock
) -> MenuHandler:
    return MenuHandler(
        service=mock_service,
        result_console_printer=mock_result_printer,
        error_console_printer=mock_error_printer,
    )


class TestMenuHandler:
    def test_init_creates_dependencies(self, mock_service: Mock) -> None:
        handler = MenuHandler(service=mock_service)
        assert isinstance(handler.dependencies, MenuDependencies)
        assert isinstance(handler.dependencies.result_printer, ResultConsolePrinter)
        assert isinstance(handler.dependencies.error_printer, ConsoleErrorHandler)

    def test_get_menu_options(self, menu_handler: MenuHandler) -> None:
        options = menu_handler.get_menu_options()
        assert isinstance(options, dict)
        assert len(options) == len(MenuOption)
        assert all(isinstance(key, str) for key in options.keys())
        assert all(isinstance(value, str) for value in options.values())

    def test_execute_invalid_option(
        self, menu_handler: Mock, mock_error_printer: Mock
    ) -> None:
        result = menu_handler.execute_option("999")

        assert result is None
        mock_error_printer.print_error.assert_called_once_with(option="999")

    def test_weekly_report_uses_live_summary_service(
        self,
        mock_service: Mock,
        mock_result_printer: Mock,
        mock_error_printer: Mock,
    ) -> None:
        summary = WeeklyActivitySummary.from_activities([])
        summary_service = Mock(spec=ActivitySummaryService)
        summary_service.generate_summary = AsyncMock(return_value=summary)
        presenter = Mock(spec=ConsoleSummaryPresenter)
        handler = MenuHandler(
            service=mock_service,
            result_console_printer=mock_result_printer,
            error_console_printer=mock_error_printer,
            summary_service=summary_service,
            summary_presenter=presenter,
        )

        result = handler.execute_option(str(MenuOption.WEEKLY_REPORT.value))

        assert result is None
        summary_service.generate_summary.assert_awaited_once_with()
        presenter.present_weekly_report.assert_called_once_with(summary)
        mock_result_printer.print_result.assert_not_called()

    def test_validate_option_success(self, menu_handler: MenuHandler) -> None:
        valid_option = "1"
        result = menu_handler._validate_option(valid_option)
        assert isinstance(result, MenuOption)
        assert result == MenuOption.ACTIVITY_DETAILS

    def test_validate_option_failure(self, menu_handler: MenuHandler) -> None:
        invalid_option = "999"
        with pytest.raises(ValueError, match="Option 999 not found"):
            menu_handler._validate_option(invalid_option)


class TestResultConsolePrinter:
    @pytest.fixture
    def printer(self) -> ResultConsolePrinter:
        return ResultConsolePrinter()

    def test_print_dataframe(
        self, printer: ResultConsolePrinter, capsys: pytest.CaptureFixture[str]
    ) -> None:
        df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        printer.print_result("1", df)
        captured = capsys.readouterr()
        assert "col1" in captured.out
        assert "col2" in captured.out

    def test_print_list(
        self, printer: ResultConsolePrinter, capsys: pytest.CaptureFixture[str]
    ) -> None:
        data = [{"name": "Activity 1"}, {"name": "Activity 2"}]
        printer.print_result("1", data)
        captured = capsys.readouterr()
        assert "Activity 1" in captured.out
        assert "Activity 2" in captured.out

    def test_print_domain_activity(
        self, printer: ResultConsolePrinter, capsys: pytest.CaptureFixture[str]
    ) -> None:
        activity = DetailedActivity.from_mapping(activity_payload())

        printer.print_result("1", [activity])

        captured = capsys.readouterr()
        assert "Morning Run" in captured.out
        assert "10.00 km" in captured.out

    def test_print_dict(
        self, printer: ResultConsolePrinter, capsys: pytest.CaptureFixture[str]
    ) -> None:
        data = {"name": "Activity 1", "distance": 1000}
        printer.print_result("1", data)
        captured = capsys.readouterr()
        assert "Activity 1" in captured.out
        assert "1.00 km" in captured.out  # Check for formatted distance

    def test_print_empty_result(
        self, printer: ResultConsolePrinter, capsys: pytest.CaptureFixture[str]
    ) -> None:
        printer.print_result(option="1", result=None)
        captured = capsys.readouterr()
        assert "No data available" in captured.out


class TestConsoleErrorHandler:
    @pytest.fixture
    def error_handler(self) -> ConsoleErrorHandler:
        return ConsoleErrorHandler()

    def test_print_error(
        self,
        error_handler: ConsoleErrorHandler,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        error_handler.print_error("999")
        captured = capsys.readouterr()

        assert "Invalid option selected" in captured.out
        assert "999" in captured.out
        assert "Please select a number from the menu or 'q' to quit" in captured.out
