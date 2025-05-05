import pandas as pd

from .exporter_interface import StreamExporter


class CsvExporter(StreamExporter):
    def export(self, df: pd.DataFrame, path: str) -> None:
        """Export stream data to CSV format."""
        df.to_csv(path, index=False)
