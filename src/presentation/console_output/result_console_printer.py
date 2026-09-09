from collections.abc import Mapping, Sequence
from typing import cast

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from src.core.service import StreamExportResult
from src.domain.activity_stream import ActivityStream, StreamBatch
from src.domain.detailed_activity import DetailedActivity
from src.domain.heart_rate_zones import HeartRateZones
from src.presentation.menu.options import MenuOption

from .console import create_console
from .formatter import ActivityFormatter

MAX_STREAM_ROWS = 20


class ResultConsolePrinter:
    def __init__(
        self,
        console: Console | None = None,
        *,
        max_stream_rows: int = MAX_STREAM_ROWS,
    ) -> None:
        if max_stream_rows < 1:
            raise ValueError("Maximum displayed stream rows must be positive.")
        self._console = console or create_console()
        self._formatter = ActivityFormatter()
        self._max_stream_rows = max_stream_rows

    def print_result(self, option: MenuOption | str, result: object) -> None:
        menu_option = _resolve_option(option)
        heading = (
            menu_option.description
            if menu_option is not None
            else f"Option {option}"
        )
        self._console.rule(
            Text.assemble(("✓ ", "success"), (heading, "heading"))
        )

        if isinstance(result, StreamExportResult):
            self._print_stream_batch(result.batch)
            self._console.print(
                Panel.fit(
                    Text.assemble(
                        ("Saved to ", "success"),
                        (str(result.path), "metric"),
                    ),
                    border_style="green",
                )
            )
        elif isinstance(result, ActivityStream):
            self._print_streams((result,))
        elif isinstance(result, StreamBatch):
            self._print_stream_batch(result)
        elif isinstance(result, HeartRateZones):
            self._print_zones(result)
        elif isinstance(result, Sequence) and not isinstance(result, (str, bytes)):
            self._print_sequence(
                result,
                detailed=menu_option
                in {
                    MenuOption.ACTIVITY_DETAILS,
                    MenuOption.ACTIVITY_DETAILS_PREV_WEEK,
                },
            )
        elif isinstance(result, Mapping):
            self._print_mapping(cast(Mapping[str, object], result))
        else:
            self._print_empty()

    def _print_sequence(
        self,
        values: Sequence[object],
        *,
        detailed: bool,
    ) -> None:
        if not values:
            self._print_empty()
            return
        if all(isinstance(value, DetailedActivity) for value in values):
            self._print_activities(
                cast(Sequence[DetailedActivity], values),
                detailed=detailed,
            )
            return

        root = Tree("[heading]Results[/heading]")
        for index, value in enumerate(values, start=1):
            branch = root.add(f"[accent]Item {index}[/accent]")
            if isinstance(value, Mapping):
                self._append_mapping(branch, cast(Mapping[str, object], value))
            else:
                branch.add(Text(str(value)))
        self._console.print(root)

    def _print_activities(
        self,
        activities: Sequence[DetailedActivity],
        *,
        detailed: bool,
    ) -> None:
        table = Table(
            title=f"Activities · {len(activities)}",
            title_style="heading",
            header_style="accent",
            border_style="bright_black",
            row_styles=("", "dim"),
        )
        table.add_column("ID", justify="right", style="muted", no_wrap=True)
        table.add_column("Activity", style="bright_white")
        table.add_column("Sport")
        table.add_column("Date", no_wrap=True)
        table.add_column("Distance", justify="right")
        table.add_column("Moving", justify="right")
        table.add_column("Avg HR", justify="right")
        if detailed:
            table.add_column("Elevation", justify="right")
            table.add_column("Speed", justify="right")
            table.add_column("Calories", justify="right")

        for activity in activities:
            values = [
                str(activity.id),
                Text(activity.name),
                Text(activity.sport_type),
                activity.start_date_local.strftime("%Y-%m-%d %H:%M"),
                self._formatter.format_value("distance", activity.distance),
                self._formatter.format_value("moving_time", activity.moving_time),
                self._format_optional_metric(
                    "average_heartrate",
                    activity.average_heartrate,
                ),
            ]
            if detailed:
                values.extend(
                    (
                        f"{activity.total_elevation_gain} m",
                        self._format_optional_metric(
                            "average_speed",
                            activity.average_speed,
                        ),
                        self._format_optional_metric("calories", activity.calories),
                    )
                )
            table.add_row(*values)
        self._console.print(table)

    def _print_stream_batch(self, batch: StreamBatch) -> None:
        self._print_streams(batch.streams)
        if batch.failures:
            failures = Table(
                title=f"Requests with errors · {len(batch.failures)}",
                title_style="warning",
                header_style="warning",
                border_style="yellow",
            )
            failures.add_column("Activity ID", justify="right")
            failures.add_column("Error")
            failures.add_column("Message")
            for failure in batch.failures:
                failures.add_row(
                    str(failure.activity_id),
                    failure.error_type,
                    failure.message,
                )
            self._console.print(failures)

    def _print_streams(self, streams: Sequence[ActivityStream]) -> None:
        rows = [row for stream in streams for row in stream.as_rows()]
        if not rows:
            self._print_empty("No stream samples available")
            return

        table = Table(
            title=f"Stream samples · {len(rows)}",
            title_style="heading",
            header_style="accent",
            border_style="bright_black",
            row_styles=("", "dim"),
        )
        table.add_column("Activity ID", justify="right")
        table.add_column("Time", justify="right")
        table.add_column("Distance", justify="right")
        table.add_column("Heart rate", justify="right")
        for row in rows[: self._max_stream_rows]:
            table.add_row(
                self._display_value(row["id"]),
                self._format_optional_metric("elapsed_time", row["time"]),
                self._format_optional_metric("distance", row["distance"]),
                self._format_optional_metric("average_heartrate", row["heartrate"]),
            )
        if len(rows) > self._max_stream_rows:
            table.caption = (
                f"Showing {self._max_stream_rows} of {len(rows)} samples. "
                "Export to CSV for the full data set."
            )
            table.caption_style = "muted"
        self._console.print(table)

    def _print_zones(self, zones: HeartRateZones) -> None:
        table = Table(
            title=f"Heart-rate zones · activity {zones.activity_id}",
            title_style="heading",
            header_style="accent",
            border_style="bright_black",
        )
        table.add_column("Zone", justify="center")
        table.add_column("Range", justify="right")
        table.add_column("Time", justify="right")
        for zone in zones.zones:
            maximum = "∞" if zone.maximum_bpm == -1 else str(zone.maximum_bpm)
            table.add_row(
                str(zone.number),
                f"{zone.minimum_bpm}–{maximum} bpm",
                self._formatter.format_value("elapsed_time", zone.time_seconds),
            )
        self._console.print(table)

    def _print_mapping(self, data: Mapping[str, object]) -> None:
        root = Tree("[heading]Activity data[/heading]")
        self._append_mapping(root, data)
        self._console.print(root)

    def _append_mapping(self, tree: Tree, data: Mapping[str, object]) -> None:
        for key, value in data.items():
            label = self._formatter.format_key(key)
            if isinstance(value, Mapping):
                branch = tree.add(Text(label, style="accent"))
                self._append_mapping(branch, cast(Mapping[str, object], value))
            elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                branch = tree.add(Text(label, style="accent"))
                for item in value:
                    if isinstance(item, Mapping):
                        child = branch.add("[muted]Item[/muted]")
                        self._append_mapping(
                            child,
                            cast(Mapping[str, object], item),
                        )
                    else:
                        branch.add(Text(str(item)))
            else:
                tree.add(
                    Text.assemble(
                        (f"{label}: ", "accent"),
                        self._formatter.format_value(key, value),
                    )
                )

    def _print_empty(self, message: str = "No data available") -> None:
        self._console.print(Panel.fit(message, border_style="yellow"))

    def _format_optional_metric(self, key: str, value: object) -> str:
        return "—" if value is None else self._formatter.format_value(key, value)

    @staticmethod
    def _display_value(value: object) -> str:
        return "—" if value is None else str(value)


def _resolve_option(option: MenuOption | str) -> MenuOption | None:
    if isinstance(option, MenuOption):
        return option
    return next(
        (candidate for candidate in MenuOption if str(candidate.id) == option),
        None,
    )
