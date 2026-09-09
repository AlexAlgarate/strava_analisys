import math
from typing import cast

import pytest

from src.domain.activity_stream import (
    ActivityStream,
    StreamBatch,
    StreamFetchFailure,
    StreamSample,
)
from tests.factories import stream_payload


def test_builds_aligned_samples_and_rows_from_uneven_streams() -> None:
    stream = ActivityStream.from_mapping(
        42,
        stream_payload(
            times=[0, 1],
            distances=[0, 10.5, 20.5],
            heart_rates=[120],
        ),
    )

    assert len(stream.samples) == 3
    assert stream.samples[1].heart_rate_bpm is None
    assert stream.samples[2].elapsed_seconds is None
    assert stream.as_rows()[0] == {
        "time": 0,
        "distance": 0.0,
        "heartrate": 120,
        "id": 42,
    }


def test_missing_streams_produce_an_empty_stream() -> None:
    stream = ActivityStream.from_mapping(1, {})

    assert stream.samples == ()
    assert stream.as_rows() == []


@pytest.mark.parametrize("activity_id", [True, 0, -1, "1"])
def test_rejects_invalid_activity_ids(activity_id: object) -> None:
    expected_error = TypeError if isinstance(activity_id, (bool, str)) else ValueError
    with pytest.raises(expected_error):
        ActivityStream(activity_id=cast(int, activity_id), samples=())


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"time": []}, "must be an object"),
        ({"time": {"data": "bad"}}, "data must be a sequence"),
        ({"time": {"data": [1.5]}}, "values must be integers"),
        ({"time": {"data": [-1]}}, "cannot be negative"),
        ({"distance": {"data": [True]}}, "values must be numeric"),
        ({"distance": {"data": [math.inf]}}, "finite and non-negative"),
    ],
)
def test_rejects_invalid_stream_values(
    payload: dict[str, object],
    message: str,
) -> None:
    with pytest.raises((TypeError, ValueError), match=message):
        ActivityStream.from_mapping(1, payload)


def test_batch_reports_counts_and_partial_state() -> None:
    stream = ActivityStream.from_mapping(1, stream_payload())
    failure = StreamFetchFailure(2, "TimeoutError", "request timed out")
    batch = StreamBatch(streams=(stream,), failures=(failure,))

    assert batch.sample_count == 3
    assert batch.is_partial
    assert len(batch.as_rows()) == 3
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
