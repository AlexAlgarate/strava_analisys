from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

from src.application.ports.export import StreamExporter
from src.application.ports.use_cases import ActivityStreamQueries
from src.application.results import StreamExportResult


class StreamExportService:
    """Export the streams for a selected week using a configured adapter."""

    def __init__(
        self,
        streams: ActivityStreamQueries,
        exporters: Mapping[str, StreamExporter],
    ) -> None:
        self._streams = streams
        self._exporters = MappingProxyType(
            {name.lower(): exporter for name, exporter in exporters.items()}
        )

    @property
    def supported_formats(self) -> tuple[str, ...]:
        return tuple(self._exporters)

    async def export_streams_for_selected_week(
        self,
        selected_format: str = "csv",
        output_dir: str | Path = ".",
        previous_week: bool = False,
    ) -> StreamExportResult:
        fmt = selected_format.lower()
        try:
            exporter = self._exporters[fmt]
        except KeyError as error:
            raise ValueError(f"Unsupported format: {fmt}") from error

        batch = await self._streams.get_weekly_streams(previous_week=previous_week)
        path = _stream_export_path(output_dir, previous_week, fmt)
        exporter.export(batch.streams, path)
        return StreamExportResult(batch=batch, path=path)


def _stream_export_path(
    output_dir: str | Path,
    previous_week: bool,
    file_format: str,
) -> Path:
    suffix = "previous_week" if previous_week else "current_week"
    return Path(output_dir) / f"streams_{suffix}.{file_format}"
