import math
from typing import cast

import pytest

from src.domain.activity_stream import (
    ActivityStream,
    StreamBatch,
    StreamFetchFailure,
    StreamSample,
)
from tests.factories import activity_stream


@pytest.mark.parametrize("activity_id", [True, 0, -1, "1"])
def test_rejects_invalid_activity_ids(activity_id: object) -> None:
    expected_error = TypeError if isinstance(activity_id, (bool, str)) else ValueError

    with pytest.raises(expected_error):
        activity_stream(cast(int, activity_id))


def test_batch_reports_counts_and_partial_state() -> None:
    stream = activity_stream()
    failure = StreamFetchFailure(2, "TimeoutError", "request timed out")
    batch = StreamBatch(streams=(stream,), failures=(failure,))

    assert batch.sample_count == 3
    assert batch.is_partial
    assert not StreamBatch().is_partial


@pytest.mark.parametrize(
    ("error_type", "message"),
    [("", "failure"), ("TimeoutError", "")],
)
def test_failure_requires_diagnostic_details(error_type: str, message: str) -> None:
    with pytest.raises(ValueError):
        StreamFetchFailure(1, error_type, message)


@pytest.mark.parametrize("field", ["error_type", "message"])
def test_failure_rejects_non_string_diagnostics(field: str) -> None:
    values: dict[str, object] = {
        "activity_id": 1,
        "error_type": "TimeoutError",
        "message": "timed out",
    }
    values[field] = 123

    with pytest.raises(TypeError, match="must be a string"):
        StreamFetchFailure(**values)  # type: ignore[arg-type]


def test_batch_rejects_duplicate_or_conflicting_outcomes() -> None:
    stream = activity_stream(1)
    failure = StreamFetchFailure(1, "TimeoutError", "timed out")

    with pytest.raises(ValueError, match="duplicate stream IDs"):
        StreamBatch(streams=(stream, stream))
    with pytest.raises(ValueError, match="duplicate failure IDs"):
        StreamBatch(failures=(failure, failure))
    with pytest.raises(ValueError, match="both successful and failed"):
        StreamBatch(streams=(stream,), failures=(failure,))


def test_batch_and_stream_require_typed_tuples() -> None:
    with pytest.raises(TypeError, match="tuple of StreamSample"):
        ActivityStream(
            1, cast(tuple[StreamSample, ...], _unknown([StreamSample(0, 0, 1)]))
        )
    with pytest.raises(TypeError, match="tuple of ActivityStream"):
        StreamBatch(
            streams=cast(tuple[ActivityStream, ...], _unknown([activity_stream()]))
        )
    with pytest.raises(TypeError, match="tuple of StreamFetchFailure"):
        StreamBatch(
            failures=cast(tuple[StreamFetchFailure, ...], _unknown((object(),)))
        )


@pytest.mark.parametrize(
    ("values", "error_type"),
    [
        ((-1, 0.0, 120), ValueError),
        ((0, -1.0, 120), ValueError),
        ((0, 0.0, -1), ValueError),
    ],
)
def test_stream_sample_rejects_negative_values(
    values: tuple[int, float, int],
    error_type: type[Exception],
) -> None:
    with pytest.raises(error_type):
        StreamSample(*values)


def test_stream_sample_rejects_non_numeric_values() -> None:
    with pytest.raises(TypeError, match="time must be an integer"):
        StreamSample(cast(int, _unknown(1.5)), 0.0, 120)
    with pytest.raises(TypeError, match="distance must be numeric"):
        StreamSample(0, cast(float, _unknown(True)), 120)


def test_stream_sample_rejects_non_finite_distance() -> None:
    with pytest.raises(ValueError, match="finite and non-negative"):
        StreamSample(0, math.inf, 120)


def test_stream_sample_requires_at_least_one_measurement() -> None:
    with pytest.raises(ValueError, match="at least one measurement"):
        StreamSample(None, None, None)


def _unknown(value: object) -> object:
    return value
