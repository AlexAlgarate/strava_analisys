from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Protocol

import pandas as pd


class StreamExporter(Protocol):
    """Persist activity stream data in one output format."""

    def export(self, data: pd.DataFrame, path: Path, /) -> None: ...


class ActivityDetailsWriter(Protocol):
    """Persist detailed activities when an explicit export is requested."""

    def write(self, activities: Sequence[Mapping[str, object]]) -> None: ...


class ActivityZonesWriter(Protocol):
    """Persist the zones associated with an activity."""

    def write(self, activity_id: int, zones: Mapping[str, object]) -> None: ...
