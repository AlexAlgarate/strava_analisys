from collections.abc import Sequence
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.application.results import ActivityZonesExportResult, StreamExportResult
from src.domain.activity_stream import ActivityStream, StreamBatch
from src.domain.detailed_activity import DetailedActivity
from src.domain.heart_rate_zones import HeartRateZones

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

    def present_heading(self, heading: str) -> None:
        self._console.rule(Text.assemble(("✓ ", "success"), (heading, "heading")))

    def present_activity_list(
        self,
        activities: Sequence[DetailedActivity],
    ) -> None:
        if not activities:
            self._print_empty()
            return

        table = self._create_activity_table(len(activities))
        for activity in activities:
            table.add_row(*self._activity_row(activity))
        self._console.print(table)

    def present_detailed_activities(
        self,
        activities: Sequence[DetailedActivity],
    ) -> None:
        if not activities:
            self._print_empty()
            return

        table = self._create_activity_table(len(activities))
        table.add_column("Elevation", justify="right")
        table.add_column("Speed", justify="right")
        table.add_column("Calories", justify="right")
        for activity in activities:
            table.add_row(
                *self._activity_row(activity),
                f"{activity.total_elevation_gain} m",
                self._format_optional_metric(
                    "average_speed",
                    activity.average_speed,
                ),
                self._format_optional_metric("calories", activity.calories),
            )
        self._console.print(table)

    def _create_activity_table(self, activity_count: int) -> Table:
        table = Table(
            title=f"Activities · {activity_count}",
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
        return table

    def _activity_row(self, activity: DetailedActivity) -> tuple[str | Text, ...]:
        return (
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
        )

    def present_activity_stream(self, stream: ActivityStream) -> None:
        self._print_streams((stream,))

    def present_stream_batch(self, batch: StreamBatch) -> None:
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

    def present_stream_export(self, result: StreamExportResult) -> None:
        self.present_stream_batch(result.batch)
        self._print_saved_path(result.path)

    def _print_streams(self, streams: Sequence[ActivityStream]) -> None:
        rows = [
            (stream.activity_id, sample)
            for stream in streams
            for sample in stream.samples
        ]
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
        for activity_id, sample in rows[: self._max_stream_rows]:
            table.add_row(
                str(activity_id),
                self._format_optional_metric(
                    "elapsed_time",
                    sample.elapsed_seconds,
                ),
                self._format_optional_metric(
                    "distance",
                    sample.distance_metres,
                ),
                self._format_optional_metric(
                    "average_heartrate",
                    sample.heart_rate_bpm,
                ),
            )
        if len(rows) > self._max_stream_rows:
            table.caption = (
                f"Showing {self._max_stream_rows} of {len(rows)} samples. "
                "Export to CSV for the full data set."
            )
            table.caption_style = "muted"
        self._console.print(table)

    def present_activity_zones(self, zones: HeartRateZones) -> None:
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
            maximum = "∞" if zone.maximum_bpm is None else str(zone.maximum_bpm)
            table.add_row(
                str(zone.number),
                f"{zone.minimum_bpm}–{maximum} bpm",
                self._formatter.format_value("elapsed_time", zone.time_seconds),
            )
        self._console.print(table)

    def present_activity_zones_export(
        self,
        result: ActivityZonesExportResult,
    ) -> None:
        self.present_activity_zones(result.zones)
        self._print_saved_path(result.path)

    def _print_saved_path(self, path: Path) -> None:
        self._console.print(
            Panel.fit(
                Text.assemble(
                    ("Saved to ", "success"),
                    (str(path), "metric"),
                ),
                border_style="green",
            )
        )

    def _print_empty(self, message: str = "No data available") -> None:
        self._console.print(Panel.fit(message, border_style="yellow"))

    def _format_optional_metric(self, key: str, value: object) -> str:
        return "—" if value is None else self._formatter.format_value(key, value)
