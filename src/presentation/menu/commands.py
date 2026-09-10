from collections.abc import Awaitable, Callable, Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Protocol

from src.presentation.menu.options import MenuOption

type CommandAction[T] = Callable[[], Awaitable[T]]
type CommandPresenter[T] = Callable[[T], None]


class RegisteredMenuCommand(Protocol):
    """Type-erased command contract consumed by the menu controller."""

    @property
    def option(self) -> MenuOption: ...

    async def execute(self) -> object: ...


@dataclass(frozen=True, slots=True)
class MenuCommand[T]:
    """Pair one menu option with a type-safe action and presenter."""

    option: MenuOption
    action: CommandAction[T]
    presenter: CommandPresenter[T]

    async def execute(self) -> T:
        result = await self.action()
        self.presenter(result)
        return result


class MenuCommandRegistry:
    """Validated lookup of the commands exposed by one CLI instance."""

    def __init__(self, commands: Iterable[RegisteredMenuCommand]) -> None:
        registered = tuple(commands)
        by_option: dict[MenuOption, RegisteredMenuCommand] = {}
        by_id: dict[str, RegisteredMenuCommand] = {}

        for command in registered:
            option = command.option
            if option in by_option:
                raise ValueError(f"Duplicate registered option: {option.name}.")

            option_id = str(option.id)
            if option_id in by_id:
                raise ValueError(f"Duplicate registered option id: {option_id}.")

            by_option[option] = command
            by_id[option_id] = command

        self._commands = registered
        self._by_id: Mapping[str, RegisteredMenuCommand] = MappingProxyType(by_id)

    @property
    def commands(self) -> tuple[RegisteredMenuCommand, ...]:
        return self._commands

    @property
    def options(self) -> tuple[MenuOption, ...]:
        return tuple(command.option for command in self._commands)

    def descriptions_by_id(self) -> dict[str, str]:
        return {
            option_id: command.option.description
            for option_id, command in self._by_id.items()
        }

    def resolve(self, option_id: str) -> RegisteredMenuCommand:
        try:
            return self._by_id[option_id]
        except KeyError as error:
            raise ValueError(f"Option {option_id} not found") from error


def with_heading[T](
    heading: str,
    heading_presenter: Callable[[str], None],
    presenter: CommandPresenter[T],
) -> CommandPresenter[T]:
    """Decorate a typed presenter with the standard command heading."""

    def present(result: T) -> None:
        heading_presenter(heading)
        presenter(result)

    return present
