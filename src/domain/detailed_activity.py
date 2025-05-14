from dataclasses import dataclass


@dataclass
class DetailedActivity:
    name: str
    distance: float
    id: int
    moving_time: int
    elapsed_time: int
    start_date_local: str
    gear_id: str
    average_heartrate: float
    max_heartrate: float
    calories: float
    perceived_exertion: int
    average_speed: float
    sport_type: str
    gear: dict[str, bool | int | float | str]
