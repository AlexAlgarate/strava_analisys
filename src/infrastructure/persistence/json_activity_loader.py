import json
from pathlib import Path
from typing import cast

from src.core.activities.summary.ports import ActivityRecord


class JsonActivityLoader:
    """Load activity records from a local JSON export."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load_activities(self) -> list[ActivityRecord]:
        with self._path.open(encoding="utf-8") as source:
            payload = json.load(source)

        if not isinstance(payload, list) or not all(
            isinstance(activity, dict) and all(isinstance(key, str) for key in activity)
            for activity in payload
        ):
            raise ValueError("Activity JSON must contain a list of objects.")
        return cast(list[ActivityRecord], payload)
