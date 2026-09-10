import os
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TextIO

_PRIVATE_DIRECTORY_MODE = 0o700
_PRIVATE_FILE_MODE = 0o600


@contextmanager
def atomic_text_file(
    path: Path,
    *,
    newline: str | None = None,
) -> Iterator[TextIO]:
    """Yield a private temporary file and atomically replace ``path`` on success."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=_PRIVATE_DIRECTORY_MODE)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)

    try:
        os.fchmod(descriptor, _PRIVATE_FILE_MODE)
        with os.fdopen(
            descriptor,
            mode="w",
            encoding="utf-8",
            newline=newline,
        ) as output:
            yield output
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        temporary_path.unlink(missing_ok=True)
        raise
