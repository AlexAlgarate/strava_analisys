from unittest.mock import AsyncMock, Mock

import pandas as pd
import pytest

from src.menu.console_error_handler import ConsoleErrorHandler
from src.menu.handler import MenuDependencies, MenuHandler
from src.menu.options import MenuOption
from src.menu.result_console_printer import ResultConsolePrinter


@pytest.fixture
def mock_service():
    service = Mock()
    service.get_one_activity = Mock()
    service.get_last_200_activities = Mock()
    service.get_activity_details = AsyncMock()
    service.get_activity_range = AsyncMock()
    service.get_streams_for_activity = AsyncMock()
    service.get_streams_for_multiple_activities = AsyncMock()
    return service


@pytest.fixture
def mock_result_printer():
    printer = Mock(spec=ResultConsolePrinter)
    printer.print_result = Mock()
    return printer


@pytest.fixture
def mock_error_printer():
    printer = Mock(spec=ConsoleErrorHandler)
    printer.print_error = Mock()
    return printer


@pytest.fixture
def menu_handler(mock_service, mock_result_printer, mock_error_printer):
    return MenuHandler(
        service=mock_service,
        result_console_printer=mock_result_printer,
        error_console_printer=mock_error_printer,
    )


class TestMenuHandler:
    def test_init_creates_dependencies(self, mock_service):
        handler = MenuHandler(service=mock_service)
        assert isinstance(handler.dependencies, MenuDependencies)
        assert isinstance(handler.dependencies.result_printer, ResultConsolePrinter)
        assert isinstance(handler.dependencies.error_printer, ConsoleErrorHandler)

    def test_get_menu_options(self, menu_handler):
        options = menu_handler.get_menu_options(MenuOption)
        assert isinstance(options, dict)
        assert len(options) == len(MenuOption)
        assert all(isinstance(key, str) for key in options.keys())
        assert all(isinstance(value, str) for value in options.values())

    def test_execute_option_one_activity(
        self, menu_handler, mock_service, mock_result_printer
    ):
        expected_result = {"id": 123, "name": "Morning Run"}
        mock_service.get_one_activity.return_value = expected_result

        result = menu_handler.execute_option("1")  # ONE_ACTIVITY option

        assert result == expected_result
        mock_service.get_one_activity.assert_called_once()
        mock_result_printer.print_result.assert_called_once_with(
            option="1", result=expected_result
        )

    def test_execute_option_last_200(
        self, menu_handler, mock_service, mock_result_printer
    ):
        expected_result = [{"id": 1}, {"id": 2}]
        mock_service.get_last_200_activities.return_value = expected_result

        result = menu_handler.execute_option("2")  # LAST_200_ACTIVITIES option

        assert result == expected_result
        mock_service.get_last_200_activities.assert_called_once()
        mock_result_printer.print_result.assert_called_once_with(
            option="2", result=expected_result
        )

    def test_execute_invalid_option(self, menu_handler, mock_error_printer):
        result = menu_handler.execute_option("999")

        assert result is None
        mock_error_printer.print_error.assert_called_once_with(option="999")

    def test_validate_option_success(self, menu_handler):
        valid_option = "1"
        result = menu_handler._validate_option(valid_option)
        assert isinstance(result, MenuOption)
        assert result == MenuOption.ONE_ACTIVITY

    def test_validate_option_failure(self, menu_handler):
        invalid_option = "999"
        with pytest.raises(ValueError, match="Option 999 not found"):
            menu_handler._validate_option(invalid_option)


class TestResultConsolePrinter:
    @pytest.fixture
    def printer(self):
        return ResultConsolePrinter()

    def test_print_dataframe(self, printer, capsys):
        df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
        printer.print_result("1", df)
        captured = capsys.readouterr()
        assert "col1" in captured.out
        assert "col2" in captured.out

    def test_print_list(self, printer, capsys):
        data = [{"name": "Activity 1"}, {"name": "Activity 2"}]
        printer.print_result("1", data)
        captured = capsys.readouterr()
        assert "Activity 1" in captured.out
        assert "Activity 2" in captured.out

    def test_print_dict(self, printer, capsys):
        data = {"name": "Activity 1", "distance": 1000}
        printer.print_result("1", data)
        captured = capsys.readouterr()
        assert "Activity 1" in captured.out
        assert "1.00 km" in captured.out  # Check for formatted distance

    def test_print_empty_result(self, printer, capsys):
        printer.print_result("1", None)
        captured = capsys.readouterr()
        assert "No data available" in captured.out


class TestConsoleErrorHandler:
    @pytest.fixture
    def error_handler(self):
        return ConsoleErrorHandler()

    def test_print_error(self, error_handler, capsys):
        error_handler.print_error("999")
        captured = capsys.readouterr()

        assert "Invalid option selected" in captured.out
        assert "999" in captured.out
        assert "Please select a number from the menu or 'q' to quit" in captured.out
