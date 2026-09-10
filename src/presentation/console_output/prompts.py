from collections.abc import Callable

from rich.console import Console

type InputReader = Callable[[str], str]


class ConsolePrompts:
    """Read and validate all interactive terminal input."""

    def __init__(
        self,
        console: Console,
        input_reader: InputReader | None = None,
    ) -> None:
        self._console = console
        self._input = input_reader or console.input

    def ask_menu_option(self) -> str:
        return (
            self._input(
                "\n[accent]Select an option[/accent] [muted](or q to quit)[/muted]: "
            )
            .strip()
            .lower()
        )

    def ask_activity_id(self) -> int:
        while True:
            raw_value = self._input("[accent]Activity ID[/accent]: ")
            try:
                return _parse_activity_id(raw_value)
            except ValueError as error:
                self._console.print(f"[error]{error}[/error]")

    def ask_activity_ids(self) -> list[int]:
        while True:
            raw_value = self._input(
                "[accent]Activity IDs[/accent] [muted](comma-separated)[/muted]: "
            )
            try:
                values = [_parse_activity_id(value) for value in raw_value.split(",")]
            except ValueError as error:
                self._console.print(f"[error]{error}[/error]")
                continue
            return list(dict.fromkeys(values))


def _parse_activity_id(raw_value: str) -> int:
    value = raw_value.strip()
    if not value:
        raise ValueError("Activity ID cannot be empty.")
    try:
        activity_id = int(value)
    except ValueError as error:
        raise ValueError("Activity ID must be a whole number.") from error
    if activity_id <= 0:
        raise ValueError("Activity ID must be positive.")
    return activity_id
