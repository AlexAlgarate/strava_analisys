import errno
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.infrastructure.export.atomic_text_file import atomic_text_file


def test_failure_after_fdopen_does_not_close_transferred_descriptor_twice(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "result.txt"
    destination.write_text("previous", encoding="utf-8")
    created_descriptors: list[int] = []
    real_mkstemp = tempfile.mkstemp

    def tracked_mkstemp(*, prefix: str, **options: Path) -> tuple[int, str]:
        descriptor, name = real_mkstemp(prefix=prefix, dir=options["dir"])
        created_descriptors.append(descriptor)
        return descriptor, name

    def interrupt_export() -> None:
        with atomic_text_file(destination) as output:
            output.write("replacement")
            raise RuntimeError("interrupted export")

    real_close = os.close
    with (
        patch(
            "src.infrastructure.export.atomic_text_file.tempfile.mkstemp",
            side_effect=tracked_mkstemp,
        ),
        patch(
            "src.infrastructure.export.atomic_text_file.os.close",
            wraps=real_close,
        ) as raw_close,
        pytest.raises(RuntimeError, match="interrupted export"),
    ):
        interrupt_export()

    raw_close.assert_not_called()
    with pytest.raises(OSError, match=os.strerror(errno.EBADF)):
        os.fstat(created_descriptors[0])
    assert destination.read_text(encoding="utf-8") == "previous"
    assert list(tmp_path.glob(f".{destination.name}.*")) == []
