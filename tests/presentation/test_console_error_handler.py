from io import StringIO

from rich.console import Console

from src.presentation.console_output.console import STRAVA_THEME
from src.presentation.console_output.console_error_handler import (
    ConsoleErrorHandler,
)


def test_print_invalid_option() -> None:
    output = StringIO()
    console = Console(file=output, theme=STRAVA_THEME, color_system=None)

    ConsoleErrorHandler(console).print_invalid_option("999")

    assert "Invalid option" in output.getvalue()
    assert "999" in output.getvalue()


def test_print_operation_error() -> None:
    output = StringIO()
    console = Console(file=output, theme=STRAVA_THEME, color_system=None)

    ConsoleErrorHandler(console).print_operation_error(
        "Load activities",
        RuntimeError("offline"),
    )

    assert "Request failed" in output.getvalue()
    assert "Load activities" in output.getvalue()
    assert "offline" in output.getvalue()


def test_sanitizes_terminal_controls_in_errors() -> None:
    output = StringIO()
    console = Console(file=output, theme=STRAVA_THEME, color_system=None)

    ConsoleErrorHandler(console).print_operation_error(
        "Load\x1b[2J activities",
        RuntimeError("offline\x07\u202e"),
    )

    rendered = output.getvalue()
    assert "\x1b[2J" not in rendered
    assert "\x07" not in rendered
    assert "\u202e" not in rendered


def test_rich_output_contains_colour_when_terminal_is_supported() -> None:
    output = StringIO()
    console = Console(
        file=output,
        theme=STRAVA_THEME,
        force_terminal=True,
        color_system="truecolor",
    )

    ConsoleErrorHandler(console).print_invalid_option("x")

    assert "\x1b[" in output.getvalue()
