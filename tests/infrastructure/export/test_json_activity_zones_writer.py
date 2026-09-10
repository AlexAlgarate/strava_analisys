import json
from pathlib import Path

from src.infrastructure.export.json_activity_zones_writer import (
    JsonActivityZonesWriter,
)
from tests.factories import heart_rate_zones


def test_writes_one_json_file_per_activity(tmp_path: Path) -> None:
    JsonActivityZonesWriter(tmp_path).write(heart_rate_zones(activity_id=123))

    with (tmp_path / "zones_123.json").open(encoding="utf-8") as source:
        assert json.load(source) == {
            "Zone_1": {"min": 0, "max": 120, "time": 300},
            "Zone_2": {"min": 120, "max": 140, "time": 600},
            "Zone_3": {"min": 140, "max": 160, "time": 900},
            "Zone_4": {"min": 160, "max": 180, "time": 400},
            "Zone_5": {"min": 180, "max": -1, "time": 120},
        }
