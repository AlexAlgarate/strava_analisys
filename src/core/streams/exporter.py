from typing import Dict

import pandas as pd

from src.core.streams.exporters.csv_exporter import CsvExporter
from src.core.streams.exporters.exporter_interface import StreamExporter


class DataExporter:
    """Handles exporting stream data to different formats."""

    def __init__(self, exporter_map: Dict[str, StreamExporter] | None = None):
        self.exporter = exporter_map or {"csv": CsvExporter()}

    def _create_path(self, output_dir: str, previous_week: bool, fmt: str) -> str:
        suffix = "previous_week" if previous_week else "current_week"
        filename = f"streams_{suffix}.{fmt}"
        return f"{output_dir}/{filename}"

    def export_streams(
        self,
        df: pd.DataFrame,
        selected_format: str = "csv",
        output_dir: str = ".",
        previous_week: bool = False,
    ) -> None:
        """Export stream data to the specified format."""

        fmt = selected_format.lower()
        if fmt not in self.exporter:
            raise ValueError(f"Unsupported format: {fmt}")

        path = self._create_path(output_dir, previous_week, fmt)
        exporter = self.exporter[fmt]
        exporter.export(df, path)
