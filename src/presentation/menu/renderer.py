from collections.abc import Iterable

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.presentation.menu.options import MenuCategory, MenuOption


class MenuRenderer:
    """Render the static menu chrome, independent from command dispatch."""

    def __init__(self, console: Console) -> None:
        self._console = console

    def print_welcome(self) -> None:
        title = Text.assemble(("STRAVA", "accent"), (" ANALYSIS", "heading"))
        self._console.print(
            Panel.fit(
                "Explore your training, streams and weekly progress.",
                title=title,
                subtitle="Python 3.13 CLI",
                border_style="#FC4C02",
                padding=(1, 3),
            )
        )

    def print_menu(self, options: Iterable[MenuOption]) -> None:
        available_options = tuple(options)
        table = Table(
            title="Choose what you want to explore",
            title_style="heading",
            header_style="accent",
            border_style="bright_black",
            show_lines=True,
        )
        table.add_column("#", justify="right", style="metric", no_wrap=True)
        table.add_column("Section", style="muted", no_wrap=True)
        table.add_column("Action", style="bright_white")
        for category in MenuCategory:
            for option in available_options:
                if option.category is category:
                    table.add_row(str(option.id), category.value, option.description)
        self._console.print(table)

    def print_goodbye(self) -> None:
        self._console.print("\n[success]✓ Session closed.[/success] See you soon! 👋")
