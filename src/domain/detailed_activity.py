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

    # Add a validation method to validate attributes of DetailedActivity
    def validate(self) -> None:
        if not self.name:
            raise ValueError("Name cannot be empty")
        if self.distance <= 0:
            raise ValueError("Distance must be greater than zero")
        if self.id <= 0:
            raise ValueError("ID must be a positive integer")
        if self.moving_time < 0 or self.elapsed_time < 0:
            raise ValueError("Time values cannot be negative")
        if not self.start_date_local:
            raise ValueError("Start date cannot be empty")
        if not self.gear_id:
            raise ValueError("Gear ID cannot be empty")
        if self.average_heartrate < 0 or self.max_heartrate < 0:
            raise ValueError("Heartrate values cannot be negative")
        if self.calories < 0:
            raise ValueError("Calories cannot be negative")
        if self.perceived_exertion < 0 or self.perceived_exertion > 10:
            raise ValueError("Perceived exertion cannot be negative")
        if self.average_speed < 0 or self.average_speed > 100:
            raise ValueError("Average speed cannot be negative")
        if not self.sport_type:
            raise ValueError("Sport type cannot be empty")
        if not isinstance(self.gear, dict):
            raise ValueError("Gear must be a dictionary")
