import json
import stat
from pathlib import Path
from unittest.mock import patch

import pytest

from src.infrastructure.export.json_activity_zones_writer import (
    JsonActivityZonesWriter,
)
from tests.factories import heart_rate_zones


def test_writes_one_json_file_per_activity(tmp_path: Path) -> None:
    path = JsonActivityZonesWriter(tmp_path).write(heart_rate_zones(activity_id=123))

    assert path == tmp_path / "zones_123.json"
    with path.open(encoding="utf-8") as source:
        assert json.load(source) == {
            "Zone_1": {"min": 0, "max": 120, "time": 300},
            "Zone_2": {"min": 120, "max": 140, "time": 600},
            "Zone_3": {"min": 140, "max": 160, "time": 900},
            "Zone_4": {"min": 160, "max": 180, "time": 400},
            "Zone_5": {"min": 180, "max": None, "time": 120},
        }
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_replaces_symlink_without_overwriting_its_target(tmp_path: Path) -> None:
    target = tmp_path / "target.json"
    target.write_text('{"keep": true}', encoding="utf-8")
    output_directory = tmp_path / "zones"
    output_directory.mkdir()
    path = output_directory / "zones_123.json"
    path.symlink_to(target)

    JsonActivityZonesWriter(output_directory).write(heart_rate_zones(123))

    assert target.read_text(encoding="utf-8") == '{"keep": true}'
    assert not path.is_symlink()


def test_failed_export_keeps_previous_file(tmp_path: Path) -> None:
    path = tmp_path / "zones_123.json"
    path.write_text('{"previous": true}', encoding="utf-8")

    with (
        patch(
            "src.infrastructure.export.json_activity_zones_writer.json.dump",
            side_effect=OSError("disk error"),
        ),
        pytest.raises(OSError, match="disk error"),
    ):
        JsonActivityZonesWriter(tmp_path).write(heart_rate_zones(123))

    assert path.read_text(encoding="utf-8") == '{"previous": true}'
