import math
from typing import cast

import pytest

from src.domain.activity_stream import StreamBatch, StreamFetchFailure, StreamSample
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


def _unknown(value: object) -> object:
    return value
