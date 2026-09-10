from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .console import create_console
from .safe_text import terminal_safe_text


class ConsoleErrorHandler:
    def __init__(self, console: Console | None = None) -> None:
        self._console = console or create_console()

    def print_invalid_option(self, option: str) -> None:
        message = Text.assemble(
            ("Invalid option: ", "error"),
            (terminal_safe_text(option), "bright_white"),
            "\nChoose one of the numbers shown in the menu.",
        )
        self._console.print(Panel.fit(message, title="Input error", border_style="red"))

    def print_operation_error(self, operation: str, error: Exception) -> None:
        message = Text.assemble(
            (f"{terminal_safe_text(operation)}\n", "heading"),
            (terminal_safe_text(str(error) or type(error).__name__), "error"),
            "\n\nYou can return to the menu and try again.",
        )
        self._console.print(
            Panel.fit(message, title="Request failed", border_style="red")
        )
