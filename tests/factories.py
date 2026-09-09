def activity_payload(
    activity_id: int = 1,
    name: str = "Morning Run",
    **overrides: object,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": activity_id,
        "name": name,
        "distance": 10_000,
        "moving_time": 3_600,
        "elapsed_time": 3_900,
        "start_date_local": "2026-09-07T07:30:00",
        "sport_type": "Run",
        "total_elevation_gain": 120,
        "average_heartrate": 145,
        "max_heartrate": 172,
        "calories": 650,
        "perceived_exertion": 6,
        "average_speed": 2.78,
    }
    payload.update(overrides)
    return payload


def stream_payload(
    *,
    times: list[int] | None = None,
    distances: list[int | float] | None = None,
    heart_rates: list[int] | None = None,
) -> dict[str, object]:
    return {
        "time": {"data": times if times is not None else [0, 1, 2]},
        "distance": {"data": distances if distances is not None else [0, 10.5, 20.5]},
        "heartrate": {
            "data": heart_rates if heart_rates is not None else [120, 125, 130]
        },
    }


def zones_payload() -> dict[str, object]:
    return {
        "distribution_buckets": [
            {"min": 0, "max": 120, "time": 300},
            {"min": 120, "max": 140, "time": 600},
            {"min": 140, "max": 160, "time": 900},
            {"min": 160, "max": 180, "time": 400},
            {"min": 180, "max": -1, "time": 120},
        ]
    }
