import json
from pathlib import Path

from src.domain.heart_rate_zones import HeartRateZones
from src.infrastructure.export.atomic_text_file import atomic_text_file


class JsonActivityZonesWriter:
    """Write each activity's zones to a dedicated JSON file."""

    def __init__(self, output_directory: Path) -> None:
        self._output_directory = output_directory

    def write(self, zones: HeartRateZones) -> Path:
        path = self._output_directory / f"zones_{zones.activity_id}.json"
        with atomic_text_file(path) as output:
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
        return path
