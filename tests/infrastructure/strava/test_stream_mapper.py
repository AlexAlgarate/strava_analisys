import math

import pytest

from src.infrastructure.strava.stream_mapper import map_activity_stream


def test_maps_present_streams_and_fills_a_missing_series() -> None:
    stream = map_activity_stream(
        42,
        {
            "time": {"data": [0, 1]},
            "distance": {"data": [0, 10.5]},
        },
    )

    assert len(stream.samples) == 2
    assert stream.samples[0].distance_metres == 0
    assert stream.samples[1].heart_rate_bpm is None


def test_rejects_present_streams_with_different_sample_counts() -> None:
    with pytest.raises(ValueError, match="same sample count"):
        map_activity_stream(
            42,
            {
                "time": {"data": [0, 1]},
                "distance": {"data": [0, 10.5, 20.5]},
            },
        )


def test_missing_streams_produce_empty_samples() -> None:
    assert map_activity_stream(1, {}).samples == ()


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ([], "response must be an object"),
        ({"time": []}, "must be an object"),
        ({"time": {}}, "data must be a sequence"),
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


def test_rejects_distance_too_large_for_float() -> None:
    with pytest.raises(ValueError, match="finite and non-negative") as error:
        map_activity_stream(1, {"distance": {"data": [10**400]}})

    assert isinstance(error.value.__cause__, OverflowError)
