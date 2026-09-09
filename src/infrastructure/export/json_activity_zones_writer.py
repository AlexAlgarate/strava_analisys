import json
from pathlib import Path

from src.domain.heart_rate_zones import HeartRateZones


class JsonActivityZonesWriter:
    """Write each activity's zones to a dedicated JSON file."""

    def __init__(self, output_directory: Path) -> None:
        self._output_directory = output_directory

    def write(self, zones: HeartRateZones) -> None:
        self._output_directory.mkdir(parents=True, exist_ok=True)
        path = self._output_directory / f"zones_{zones.activity_id}.json"
        with path.open("w", encoding="utf-8") as output:
            json.dump(
                {
                    f"Zone_{zone.number}": {
                        "min": zone.minimum_bpm,
                        "max": zone.maximum_bpm,
                        "time": zone.time_seconds,
                    }
                    for zone in zones.zones
                },
                output,
                ensure_ascii=False,
                indent=4,
            )
