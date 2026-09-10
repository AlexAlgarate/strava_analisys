import csv
import stat
from pathlib import Path
from unittest.mock import patch

import pytest

from src.infrastructure.export.csv_stream_exporter import CsvStreamExporter
from tests.factories import activity_stream


def test_writes_stream_samples_and_creates_parent_directory(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "streams.csv"

    CsvStreamExporter().export((activity_stream(),), path)

    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    assert len(rows) == 3
    assert rows[0] == {
        "time": "0",
        "distance": "0.0",
        "heartrate": "120",
        "id": "1",
    }
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_replaces_symlink_without_overwriting_its_target(tmp_path: Path) -> None:
    target = tmp_path / "target.txt"
    target.write_text("keep me", encoding="utf-8")
    path = tmp_path / "streams.csv"
    path.symlink_to(target)

    CsvStreamExporter().export((activity_stream(),), path)

    assert target.read_text(encoding="utf-8") == "keep me"
    assert not path.is_symlink()


def test_failed_export_keeps_previous_file(tmp_path: Path) -> None:
    path = tmp_path / "streams.csv"
    path.write_text("previous", encoding="utf-8")

    with (
        patch.object(csv.DictWriter, "writerows", side_effect=OSError("disk error")),
        pytest.raises(OSError, match="disk error"),
    ):
        CsvStreamExporter().export((activity_stream(),), path)

    assert path.read_text(encoding="utf-8") == "previous"
