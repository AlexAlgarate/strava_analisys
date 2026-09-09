from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.domain.activity_summary import WeeklyActivitySummary

from .console import create_console


class ConsoleSummaryPresenter:
    """Render a weekly activity summary in the terminal."""

    def __init__(self, console: Console | None = None) -> None:
        self._console = console or create_console()

    def present_weekly_report(self, summary: WeeklyActivitySummary) -> None:
        metrics = Table.grid(padding=(0, 2))
        metrics.add_column(style="bright_white")
        metrics.add_column(justify="right", style="metric")
        metrics.add_row("Activities", str(summary.activity_count))
        metrics.add_row("Total distance", f"{summary.total_distance_km} km")
        metrics.add_row("Moving time", str(summary.total_moving_time))
        metrics.add_row("Elevation gain", f"{summary.total_elevation_gain} m")
        metrics.add_row(
            "Average heart rate",
            _format_optional(summary.average_heartrate, "bpm"),
        )
        metrics.add_row(
            "Average max heart rate",
            _format_optional(summary.average_max_heartrate, "bpm"),
        )
        metrics.add_row("Calories", f"{summary.total_calories} kcal")
        metrics.add_row(
            "Perceived exertion",
            _format_optional(summary.average_perceived_exertion),
        )
        self._console.print(
            Panel(
                metrics,
                title="[accent]Weekly training summary[/accent]",
                border_style="#FC4C02",
                expand=False,
            )
        )


def _format_optional(value: float | None, unit: str = "") -> str:
    if value is None:
        return "N/A"
    suffix = f" {unit}" if unit else ""
    return f"{value}{suffix}"
