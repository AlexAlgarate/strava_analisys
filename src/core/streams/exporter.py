from collections.abc import Mapping
from pathlib import Path

import pandas as pd

from src.core.ports.export import StreamExporter


class DataExporter:
    """Handles exporting stream data to different formats."""

    def __init__(self, exporters: Mapping[str, StreamExporter]) -> None:
        self.exporters = {
            name.lower(): exporter for name, exporter in exporters.items()
        }

    def _create_path(
        self, output_dir: str | Path, previous_week: bool, file_format: str
    ) -> Path:
        suffix = "previous_week" if previous_week else "current_week"
        filename = f"streams_{suffix}.{file_format}"
        return Path(output_dir) / filename

    def export_streams(
        self,
        df: pd.DataFrame,
        selected_format: str = "csv",
        output_dir: str | Path = ".",
        previous_week: bool = False,
    ) -> None:
        """Export stream data to the specified format."""

        fmt = selected_format.lower()
        if fmt not in self.exporters:
            raise ValueError(f"Unsupported format: {fmt}")

        path = self._create_path(output_dir, previous_week, fmt)
        exporter = self.exporters[fmt]
        exporter.export(df, path)
