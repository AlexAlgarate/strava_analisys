import re
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

from src.application.ports.export import StreamExporter
from src.application.ports.use_cases import ActivityStreamQueries
from src.application.results import StreamExportResult
from src.domain.week_period import WeekSelection


class StreamExportService:
    """Export the streams for a selected week using a configured adapter."""

    def __init__(
        self,
        streams: ActivityStreamQueries,
        exporters: Mapping[str, StreamExporter],
    ) -> None:
        normalized_exporters: dict[str, StreamExporter] = {}
        for name, exporter in exporters.items():
            normalized_name = _normalize_format(name)
            if normalized_name in normalized_exporters:
                raise ValueError(f"Duplicate stream export format: {normalized_name}")
            normalized_exporters[normalized_name] = exporter
        if not normalized_exporters:
            raise ValueError("At least one stream exporter must be configured.")
        self._streams = streams
        self._exporters = MappingProxyType(normalized_exporters)

    @property
    def supported_formats(self) -> tuple[str, ...]:
        return tuple(self._exporters)

    async def export_streams_for_selected_week(
        self,
        selected_format: str = "csv",
        output_dir: str | Path = ".",
        *,
        week: WeekSelection,
    ) -> StreamExportResult:
        fmt = _normalize_format(selected_format)
        try:
            exporter = self._exporters[fmt]
        except KeyError as error:
            raise ValueError(f"Unsupported format: {fmt}") from error

        batch = await self._streams.get_weekly_streams(week=week)
        path = _stream_export_path(output_dir, fmt, week=week)
        exporter.export(batch.streams, path)
        return StreamExportResult(batch=batch, path=path)


def _stream_export_path(
    output_dir: str | Path,
    file_format: str,
    *,
    week: WeekSelection,
) -> Path:
    suffix = f"{week.value}_week"
    return Path(output_dir) / f"streams_{suffix}.{file_format}"


def _normalize_format(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("Stream export format must be a string.")
    normalized = value.strip().lower()
    if re.fullmatch(r"[a-z0-9]+(?:[-_][a-z0-9]+)*", normalized) is None:
        raise ValueError("Stream export format must be a safe file extension.")
    return normalized
