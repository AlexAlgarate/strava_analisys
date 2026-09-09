import json
from collections.abc import Mapping
from pathlib import Path


class JsonActivityZonesWriter:
    """Write each activity's zones to a dedicated JSON file."""

    def __init__(self, output_directory: Path) -> None:
        self._output_directory = output_directory

    def write(self, activity_id: int, zones: Mapping[str, object]) -> None:
        self._output_directory.mkdir(parents=True, exist_ok=True)
        path = self._output_directory / f"zones_{activity_id}.json"
        with path.open("w", encoding="utf-8") as output:
            json.dump(zones, output, ensure_ascii=False, indent=4)
