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

    def validate(self) -> None:
        validation_rules = {
            "name": lambda x: bool(x),
            "distance": lambda x: x > 0,
            "id": lambda x: x > 0,
            "moving_time": lambda x: x >= 0,
            "elapsed_time": lambda x: x >= 0,
            "start_date_local": lambda x: bool(x),
            "gear_id": lambda x: bool(x),
            "average_heartrate": lambda x: x >= 0,
            "max_heartrate": lambda x: x >= 0,
            "calories": lambda x: x >= 0,
            "perceived_exertion": lambda x: 0 <= x <= 10,
            "average_speed": lambda x: 0 <= x <= 100,
            "sport_type": lambda x: bool(x),
            "gear": lambda x: isinstance(x, dict),
        }

        for attribute, rule in validation_rules.items():
            value = getattr(self, attribute)
            if not rule(value):
                raise ValueError(f"Invalid value for {attribute}: {value}")
