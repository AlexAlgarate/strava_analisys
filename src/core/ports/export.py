from collections.abc import Mapping
from pathlib import Path
from typing import Protocol

import pandas as pd


class StreamExporter(Protocol):
    """Persist activity stream data in one output format."""

    def export(self, data: pd.DataFrame, path: Path, /) -> None: ...


class ActivityZonesWriter(Protocol):
    """Persist the zones associated with an activity."""

    def write(self, activity_id: int, zones: Mapping[str, object]) -> None: ...
