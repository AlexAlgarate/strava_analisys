from collections.abc import Callable, Sequence
from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console

from src.application.results import ActivityZonesExportResult, StreamExportResult
from src.domain.activity_stream import StreamBatch, StreamFetchFailure
from src.domain.detailed_activity import DetailedActivity
from src.presentation.console_output.console import STRAVA_THEME
from src.presentation.console_output.result_console_printer import (
    ResultConsolePrinter,
)
from tests.factories import activity_model, activity_stream, heart_rate_zones


@pytest.fixture
def output() -> StringIO:
    return StringIO()


@pytest.fixture
def console(output: StringIO) -> Console:
    return Console(
        file=output,
        theme=STRAVA_THEME,
        color_system=None,
        width=120,
    )


@pytest.fixture
def printer(console: Console) -> ResultConsolePrinter:
    return ResultConsolePrinter(console, max_stream_rows=2)


def test_presents_command_heading(
    printer: ResultConsolePrinter,
    output: StringIO,
) -> None:
    printer.present_heading("View one activity stream")

    assert "✓ View one activity stream" in output.getvalue()


def test_presents_activity_stream_and_truncation(
    printer: ResultConsolePrinter,
    output: StringIO,
) -> None:
    printer.present_activity_stream(activity_stream(7))

    rendered = output.getvalue()
    assert "Heart rate" in rendered
    assert "120" in rendered
    assert "Showing 2 of 3 samples" in rendered


def test_presents_stream_batch_failures(
    printer: ResultConsolePrinter,
    output: StringIO,
) -> None:
    batch = StreamBatch(failures=(StreamFetchFailure(7, "TimeoutError", "timed out"),))

    printer.present_stream_batch(batch)

    rendered = output.getvalue()
    assert "Activity ID" in rendered
    assert "timed out" in rendered


def test_presents_stream_export_result(
    printer: ResultConsolePrinter,
    output: StringIO,
) -> None:
    result = StreamExportResult(StreamBatch(), Path("streams.csv"))

    printer.present_stream_export(result)

    assert "Saved to" in output.getvalue()
    assert "streams.csv" in output.getvalue()


def test_presents_compact_activity_list(
    printer: ResultConsolePrinter,
    output: StringIO,
) -> None:
    printer.present_activity_list([activity_model()])

    rendered = output.getvalue()
    assert "Morning Run" in rendered
    assert "10.00 km" in rendered
    assert "Calories" not in rendered


def test_presents_detailed_activity_list(
    printer: ResultConsolePrinter,
    output: StringIO,
) -> None:
    printer.present_detailed_activities([activity_model()])

    rendered = output.getvalue()
    assert "Morning Run" in rendered
    assert "10.00 km" in rendered
    assert "Calories" in rendered


@pytest.mark.parametrize(
    "present",
    [
        lambda printer, activities: printer.present_activity_list(activities),
        lambda printer, activities: printer.present_detailed_activities(activities),
    ],
)
def test_presents_empty_activity_collections(
    printer: ResultConsolePrinter,
    output: StringIO,
    present: Callable[
        [ResultConsolePrinter, Sequence[DetailedActivity]],
        None,
    ],
) -> None:
    present(printer, [])

    assert "No data available" in output.getvalue()


def test_presents_activity_zones(
    printer: ResultConsolePrinter,
    output: StringIO,
) -> None:
    printer.present_activity_zones(heart_rate_zones(7))

    rendered = output.getvalue()
    assert "Heart-rate zones · activity 7" in rendered
    assert "180–∞ bpm" in rendered


def test_presents_activity_zones_export_result(
    printer: ResultConsolePrinter,
    output: StringIO,
) -> None:
    zones = heart_rate_zones(7)

    printer.present_activity_zones_export(
        ActivityZonesExportResult(zones, Path("zones_7.json"))
    )

    rendered = output.getvalue()
    assert "Heart-rate zones · activity 7" in rendered
    assert "Saved to" in rendered
    assert "zones_7.json" in rendered


def test_rejects_invalid_row_limit(console: Console) -> None:
    with pytest.raises(ValueError, match="must be positive"):
        ResultConsolePrinter(console, max_stream_rows=0)
