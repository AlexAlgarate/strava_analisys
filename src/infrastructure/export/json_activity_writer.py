import json
from collections.abc import Mapping, Sequence
from pathlib import Path


class JsonActivityDetailsWriter:
    """Write detailed activity responses to one JSON file."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def write(self, activities: Sequence[Mapping[str, object]]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as output:
            json.dump(activities, output, ensure_ascii=False, indent=4)


class JsonActivityZonesWriter:
    """Write each activity's zones to a dedicated JSON file."""

    def __init__(self, output_directory: Path) -> None:
        self._output_directory = output_directory

    def write(self, activity_id: int, zones: Mapping[str, object]) -> None:
        self._output_directory.mkdir(parents=True, exist_ok=True)
        path = self._output_directory / f"zones_{activity_id}.json"
        with path.open("w", encoding="utf-8") as output:
            json.dump(zones, output, ensure_ascii=False, indent=4)
