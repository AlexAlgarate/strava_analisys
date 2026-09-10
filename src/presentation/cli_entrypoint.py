import logging
from dataclasses import dataclass

from src.presentation.menu.commands import MenuCommandRegistry
from src.presentation.ports import (
    ErrorPresenter,
    MenuView,
    OperationProgress,
    PromptReader,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class MenuDependencies:
    commands: MenuCommandRegistry
    error_printer: ErrorPresenter
    prompts: PromptReader
    menu_view: MenuView
    progress: OperationProgress


class MenuHandler:
    def __init__(self, dependencies: MenuDependencies) -> None:
        self.dependencies = dependencies

    def ask_option(self) -> str:
        return self.dependencies.prompts.ask_menu_option()

    async def execute_option(self, option: str) -> object | None:
        try:
            command = self.dependencies.commands.resolve(option)
        except ValueError:
            self.dependencies.error_printer.print_invalid_option(option)
            return None

        try:
            with self.dependencies.progress.track(command.option.description):
                return await command.execute()
        except EOFError:
            raise
        except Exception as error:
            logger.exception("Menu operation failed: %s", command.option.description)
            self.dependencies.error_printer.print_operation_error(
                command.option.description,
                error,
            )
            return None

    def print_welcome(self) -> None:
        self.dependencies.menu_view.print_welcome()

    def print_menu(self) -> None:
        self.dependencies.menu_view.print_menu(self.dependencies.commands.options)

    def print_goodbye(self) -> None:
        self.dependencies.menu_view.print_goodbye()
