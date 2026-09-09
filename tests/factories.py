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
