from collections.abc import Awaitable, Callable
from unittest.mock import AsyncMock, Mock

import pytest

from src.presentation.menu.commands import MenuCommand, MenuCommandRegistry
from src.presentation.menu.options import MenuOption


def _command(
    option: MenuOption,
    *,
    action: Callable[[], Awaitable[str]] | None = None,
    presenter: Callable[[str], None] | None = None,
) -> MenuCommand[str]:
    return MenuCommand(
        option=option,
        action=action or AsyncMock(return_value="result"),
        presenter=presenter or Mock(),
    )


@pytest.mark.asyncio
async def test_command_presents_the_value_returned_by_its_action() -> None:
    action = AsyncMock(return_value="result")
    presenter = Mock()

    result = await _command(
        MenuOption.ACTIVITY_DETAILS,
        action=action,
        presenter=presenter,
    ).execute()

    assert result == "result"
    action.assert_awaited_once_with()
    presenter.assert_called_once_with("result")


def test_registry_can_expose_an_intentional_subset() -> None:
    command = _command(MenuOption.ACTIVITY_ZONES)

    registry = MenuCommandRegistry((command,))

    assert registry.commands == (command,)
    assert registry.options == (MenuOption.ACTIVITY_ZONES,)
    assert registry.resolve("10") is command


def test_registry_rejects_a_duplicate_option() -> None:
    command = _command(MenuOption.ACTIVITY_DETAILS)

    with pytest.raises(ValueError, match="Duplicate registered option"):
        MenuCommandRegistry((command, command))


def test_registry_rejects_distinct_options_with_the_same_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        MenuOption.ACTIVITY_LIST,
        "_option_id",
        MenuOption.ACTIVITY_DETAILS.id,
    )

    with pytest.raises(ValueError, match="Duplicate registered option id: 1"):
        MenuCommandRegistry(
            (
                _command(MenuOption.ACTIVITY_DETAILS),
                _command(MenuOption.ACTIVITY_LIST),
            )
        )


def test_registry_rejects_an_unknown_id() -> None:
    registry = MenuCommandRegistry((_command(MenuOption.ACTIVITY_DETAILS),))

    with pytest.raises(ValueError, match="Option 999 not found"):
        registry.resolve("999")
