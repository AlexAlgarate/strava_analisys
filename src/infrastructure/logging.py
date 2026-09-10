import logging
import os
from io import TextIOWrapper
from pathlib import Path
from typing import TextIO, override

FORMAT_LOGGING = (
    "%(levelname)s -- %(asctime)s -- %(name)s -- %(funcName)s : %(message)s"
)
DATEFMT_LOGGING = "%y-%m-%d %H:%M:%S"
_PRIVATE_DIRECTORY_MODE = 0o700
_PRIVATE_FILE_MODE = 0o600


class _ApplicationStreamHandler(logging.StreamHandler[TextIO]):
    """Console handler owned by this application."""


class _ApplicationFileHandler(logging.FileHandler):
    """File handler owned by this application."""

    @override
    def _open(self) -> TextIOWrapper:
        flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT
        flags |= getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(self.baseFilename, flags, _PRIVATE_FILE_MODE)
        try:
            os.fchmod(descriptor, _PRIVATE_FILE_MODE)
            return open(
                descriptor,
                mode="a",
                encoding=self.encoding,
                errors=self.errors,
                closefd=True,
            )
        except (OSError, ValueError):
            os.close(descriptor)
            raise


def setup_logging(
    level: int = logging.INFO,
    *,
    log_file: Path | None = None,
) -> Path:
    """Configure application logging idempotently and return the log path."""
    logger = logging.getLogger()
    logger.setLevel(level)
    formatter = logging.Formatter(fmt=FORMAT_LOGGING, datefmt=DATEFMT_LOGGING)

    for handler in logger.handlers[:]:
        if isinstance(handler, (_ApplicationStreamHandler, _ApplicationFileHandler)):
            handler.close()
            logger.removeHandler(handler)

    console_handler = _ApplicationStreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    uses_default_directory = log_file is None
    resolved_log_file = log_file or _default_log_file()
    _prepare_log_directory(
        resolved_log_file.parent,
        restrict_existing=uses_default_directory,
    )
    file_handler = _ApplicationFileHandler(resolved_log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return resolved_log_file


def _prepare_log_directory(directory: Path, *, restrict_existing: bool) -> None:
    existed = directory.exists()
    if directory.is_symlink():
        raise OSError(f"Refusing to use a symbolic link as log directory: {directory}")
    directory.mkdir(mode=_PRIVATE_DIRECTORY_MODE, parents=True, exist_ok=True)
    if restrict_existing or not existed:
        directory.chmod(_PRIVATE_DIRECTORY_MODE)


def _default_log_file() -> Path:
    state_home = os.getenv("XDG_STATE_HOME")
    base_directory = (
        Path(state_home).expanduser()
        if state_home
        else Path.home() / ".local" / "state"
    )
    return base_directory / "strava-analysis" / "application.log"
