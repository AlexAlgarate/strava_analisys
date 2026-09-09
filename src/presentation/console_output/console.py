from rich.console import Console
from rich.theme import Theme

STRAVA_THEME = Theme(
    {
        "accent": "bold #FC4C02",
        "heading": "bold bright_white",
        "muted": "dim cyan",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "metric": "bold bright_cyan",
    }
)


def create_console() -> Console:
    """Create the shared Rich console used by the CLI."""
    return Console(theme=STRAVA_THEME, highlight=False)
