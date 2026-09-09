from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

from src.core.ports.export import StreamExporter
from src.domain.activity_stream import ActivityStream


class DataExporter:
    """Handles exporting stream data to different formats."""

    def __init__(self, exporters: Mapping[str, StreamExporter]) -> None:
        self._exporters = MappingProxyType(
            {name.lower(): exporter for name, exporter in exporters.items()}
        )

    @property
    def supported_formats(self) -> tuple[str, ...]:
        return tuple(self._exporters)

    def _create_path(
        self, output_dir: str | Path, previous_week: bool, file_format: str
    ) -> Path:
        suffix = "previous_week" if previous_week else "current_week"
        filename = f"streams_{suffix}.{file_format}"
        return Path(output_dir) / filename

    def export_streams(
        self,
        streams: tuple[ActivityStream, ...],
        selected_format: str = "csv",
        output_dir: str | Path = ".",
        previous_week: bool = False,
    ) -> Path:
        """Export stream data to the specified format."""

        fmt = selected_format.lower()
        if fmt not in self._exporters:
            raise ValueError(f"Unsupported format: {fmt}")

        path = self._create_path(output_dir, previous_week, fmt)
        exporter = self._exporters[fmt]
        exporter.export(streams, path)
        return path
