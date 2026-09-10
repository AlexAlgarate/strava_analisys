import math

import pytest

from src.infrastructure.strava.stream_mapper import map_activity_stream
from tests.factories import stream_payload


def test_maps_and_aligns_uneven_streams() -> None:
    stream = map_activity_stream(
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


def test_missing_streams_produce_empty_samples() -> None:
    assert map_activity_stream(1, {}).samples == ()


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ([], "response must be an object"),
        ({"time": []}, "must be an object"),
        ({"time": {"data": "bad"}}, "data must be a sequence"),
        ({"time": {"data": [1.5]}}, "values must be integers"),
        ({"time": {"data": [-1]}}, "cannot be negative"),
        ({"distance": {"data": [True]}}, "values must be numeric"),
        ({"distance": {"data": [math.inf]}}, "finite and non-negative"),
    ],
)
def test_rejects_invalid_stream_payloads(payload: object, message: str) -> None:
    with pytest.raises((TypeError, ValueError), match=message):
        map_activity_stream(1, payload)
