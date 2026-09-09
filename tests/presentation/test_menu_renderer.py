from io import StringIO

from rich.console import Console

from src.presentation.console_output.console import STRAVA_THEME
from src.presentation.menu.options import MenuOption
from src.presentation.menu.renderer import MenuRenderer


def test_renders_welcome_grouped_menu_and_goodbye() -> None:
    output = StringIO()
    console = Console(
        file=output,
        theme=STRAVA_THEME,
        color_system=None,
        width=120,
    )
    renderer = MenuRenderer(console)

    renderer.print_welcome()
    renderer.print_menu(MenuOption)
    renderer.print_goodbye()

    rendered = output.getvalue()
    assert "STRAVA ANALYSIS" in rendered
    assert "Choose what you want to explore" in rendered
    assert "Activities" in rendered
    assert "Streams & exports" in rendered
    assert "Insights" in rendered
    assert "Session closed" in rendered
