from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console

from src.core.service import StreamExportResult
from src.domain.activity_stream import ActivityStream, StreamBatch, StreamFetchFailure
from src.domain.detailed_activity import DetailedActivity
from src.domain.heart_rate_zones import HeartRateZones
from src.presentation.console_output.console import STRAVA_THEME
from src.presentation.console_output.result_console_printer import (
    ResultConsolePrinter,
)
from src.presentation.menu.options import MenuOption
from tests.factories import activity_payload, stream_payload, zones_payload


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


def test_print_activity_stream_and_truncation(
    printer: ResultConsolePrinter,
    output: StringIO,
) -> None:
    stream = ActivityStream.from_mapping(7, stream_payload())

    printer.print_result(MenuOption.SINGLE_STREAM, stream)

    rendered = output.getvalue()
    assert "Heart rate" in rendered
    assert "120" in rendered
    assert "Showing 2 of 3 samples" in rendered


def test_print_stream_batch_failures(
    printer: ResultConsolePrinter,
    output: StringIO,
) -> None:
    batch = StreamBatch(failures=(StreamFetchFailure(7, "TimeoutError", "timed out"),))

    printer.print_result(MenuOption.MULTIPLE_STREAMS, batch)

    rendered = output.getvalue()
    assert "Activity ID" in rendered
    assert "timed out" in rendered


def test_print_export_result(
    printer: ResultConsolePrinter,
    output: StringIO,
) -> None:
    result = StreamExportResult(StreamBatch(), Path("streams.csv"))

    printer.print_result(MenuOption.STREAMS_CURRENT_WEEK, result)

    assert "Saved to" in output.getvalue()
    assert "streams.csv" in output.getvalue()


@pytest.mark.parametrize(
    "option",
    [MenuOption.ACTIVITY_DETAILS, MenuOption.ACTIVITY_RANGE],
)
def test_print_activity_list(
    printer: ResultConsolePrinter,
    output: StringIO,
    option: MenuOption,
) -> None:
    activity = DetailedActivity.from_mapping(activity_payload())

    printer.print_result(option, [activity])

    rendered = output.getvalue()
    assert "Morning Run" in rendered
    assert "10.00 km" in rendered
    assert ("Calories" in rendered) is (option is MenuOption.ACTIVITY_DETAILS)


def test_print_generic_sequence(
    printer: ResultConsolePrinter,
    output: StringIO,
) -> None:
    printer.print_result(
        MenuOption.ACTIVITY_RANGE,
        [{"name": "Activity 1"}, "note"],
    )

    rendered = output.getvalue()
    assert "Activity 1" in rendered
    assert "note" in rendered


def test_print_nested_mapping(
    printer: ResultConsolePrinter,
    output: StringIO,
) -> None:
    printer.print_result(
        MenuOption.ACTIVITY_RANGE,
        {
            "gear": {"name": "Daily Trainer"},
            "laps": [{"distance": 1_000}, "recovery"],
        },
    )

    rendered = output.getvalue()
    assert "Daily Trainer" in rendered
    assert "1.00 km" in rendered
    assert "recovery" in rendered


def test_print_zones(
    printer: ResultConsolePrinter,
    output: StringIO,
) -> None:
    zones = HeartRateZones.from_api_response(7, zones_payload())

    printer.print_result(MenuOption.ACTIVITY_ZONES, zones)

    rendered = output.getvalue()
    assert "Heart-rate zones · activity 7" in rendered
    assert "180–∞ bpm" in rendered


@pytest.mark.parametrize("result", [None, [], object()])
def test_print_empty_or_unknown_result(
    printer: ResultConsolePrinter,
    output: StringIO,
    result: object,
) -> None:
    printer.print_result(MenuOption.ACTIVITY_RANGE, result)

    assert "No data available" in output.getvalue()


def test_rejects_invalid_row_limit(console: Console) -> None:
    with pytest.raises(ValueError, match="must be positive"):
        ResultConsolePrinter(console, max_stream_rows=0)
