from collections.abc import Generator
from contextlib import contextmanager

from rich.console import Console


class ConsoleProgress:
    """Show transient progress while a terminal operation is running."""

    def __init__(self, console: Console) -> None:
        self._console = console

    @contextmanager
    def track(self, description: str) -> Generator[None]:
        with self._console.status(
            f"[accent]{description}…[/accent]",
            spinner="dots",
        ):
            yield
