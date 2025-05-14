import pandas as pd

from src.interfaces.stream_exporter import IStreamExporter


class CsvExporter(IStreamExporter):
    def export(self, df: pd.DataFrame, path: str) -> None:
        """Export stream data to CSV format."""
        df.to_csv(path, index=False)
