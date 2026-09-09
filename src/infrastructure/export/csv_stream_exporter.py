from pathlib import Path

import pandas as pd


class CsvStreamExporter:
    """Write activity stream data as CSV."""

    def export(self, data: pd.DataFrame, path: Path) -> None:
        data.to_csv(path, index=False)
