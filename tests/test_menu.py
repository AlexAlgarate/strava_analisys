import logging
from contextlib import nullcontext
from unittest.mock import AsyncMock, Mock

import pytest

from src.presentation.cli_entrypoint import MenuDependencies, MenuHandler
from src.presentation.menu.commands import MenuCommand, MenuCommandRegistry
from src.presentation.menu.options import MenuOption
from src.presentation.ports import (
    ErrorPresenter,
    MenuView,
    OperationProgress,
    PromptReader,
)


@pytest.fixture
def action() -> AsyncMock:
    return AsyncMock(return_value="result")


@pytest.fixture
def presenter() -> Mock:
    return Mock()


@pytest.fixture
def command(action: AsyncMock, presenter: Mock) -> MenuCommand[str]:
    return MenuCommand(
        option=MenuOption.ACTIVITY_DETAILS,
        action=action,
        presenter=presenter,
    )


@pytest.fixture
def commands(command: MenuCommand[str]) -> MenuCommandRegistry:
    return MenuCommandRegistry((command,))


@pytest.fixture
def error_presenter() -> Mock:
    return Mock(spec=ErrorPresenter)


@pytest.fixture
def prompts() -> Mock:
    result = Mock(spec=PromptReader)
    result.ask_menu_option.return_value = "1"
    return result


@pytest.fixture
def menu_view() -> Mock:
    return Mock(spec=MenuView)


@pytest.fixture
def progress() -> Mock:
    result = Mock(spec=OperationProgress)
    result.track.return_value = nullcontext()
    return result


@pytest.fixture
def menu_handler(
    commands: MenuCommandRegistry,
    error_presenter: Mock,
    prompts: Mock,
    menu_view: Mock,
    progress: Mock,
) -> MenuHandler:
    return MenuHandler(
        MenuDependencies(
            commands=commands,
            error_printer=error_presenter,
            prompts=prompts,
            menu_view=menu_view,
            progress=progress,
        )
    )


def test_reads_an_option_from_the_prompt(
    menu_handler: MenuHandler,
    prompts: Mock,
) -> None:
    assert menu_handler.ask_option() == "1"
    prompts.ask_menu_option.assert_called_once_with()


@pytest.mark.asyncio
async def test_rejects_an_unregistered_option_without_executing_a_command(
    menu_handler: MenuHandler,
    action: AsyncMock,
    error_presenter: Mock,
) -> None:
    result = await menu_handler.execute_option("999")

    assert result is None
    action.assert_not_awaited()
    error_presenter.print_invalid_option.assert_called_once_with("999")


@pytest.mark.asyncio
async def test_executes_and_presents_the_selected_command(
    menu_handler: MenuHandler,
    action: AsyncMock,
    presenter: Mock,
    progress: Mock,
) -> None:
    result = await menu_handler.execute_option("1")

    assert result == "result"
    action.assert_awaited_once_with()
    presenter.assert_called_once_with("result")
    progress.track.assert_called_once_with(MenuOption.ACTIVITY_DETAILS.description)


@pytest.mark.asyncio
async def test_reports_action_errors_without_presenting_a_result(
    menu_handler: MenuHandler,
    action: AsyncMock,
    presenter: Mock,
    error_presenter: Mock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    error = RuntimeError("Strava is unavailable")
    action.side_effect = error

    with caplog.at_level(logging.ERROR, logger="src.presentation.cli_entrypoint"):
        result = await menu_handler.execute_option("1")

    assert result is None
    assert "Menu operation failed" in caplog.text
    presenter.assert_not_called()
    error_presenter.print_operation_error.assert_called_once_with(
        MenuOption.ACTIVITY_DETAILS.description,
        error,
    )


@pytest.mark.asyncio
async def test_reports_presenter_errors_through_the_same_operation_boundary(
    menu_handler: MenuHandler,
    presenter: Mock,
    error_presenter: Mock,
) -> None:
    error = RuntimeError("console unavailable")
    presenter.side_effect = error

    result = await menu_handler.execute_option("1")

    assert result is None
    error_presenter.print_operation_error.assert_called_once_with(
        MenuOption.ACTIVITY_DETAILS.description,
        error,
    )


@pytest.mark.asyncio
async def test_propagates_end_of_input_from_a_command(
    menu_handler: MenuHandler,
    action: AsyncMock,
    presenter: Mock,
    error_presenter: Mock,
) -> None:
    action.side_effect = EOFError()

    with pytest.raises(EOFError):
        await menu_handler.execute_option("1")

    presenter.assert_not_called()
    error_presenter.print_operation_error.assert_not_called()


def test_renders_only_registered_options_and_menu_chrome(
    menu_handler: MenuHandler,
    menu_view: Mock,
) -> None:
    menu_handler.print_welcome()
    menu_handler.print_menu()
    menu_handler.print_goodbye()

    menu_view.print_welcome.assert_called_once_with()
    menu_view.print_menu.assert_called_once_with((MenuOption.ACTIVITY_DETAILS,))
    menu_view.print_goodbye.assert_called_once_with()
