import logging
import os
from pathlib import Path
from typing import TextIO

FORMAT_LOGGING = (
    "%(levelname)s -- %(asctime)s -- %(name)s -- %(funcName)s : %(message)s"
)
DATEFMT_LOGGING = "%y-%m-%d %H:%M:%S"


class _ApplicationStreamHandler(logging.StreamHandler[TextIO]):
    """Console handler owned by this application."""


class _ApplicationFileHandler(logging.FileHandler):
    """File handler owned by this application."""


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

    resolved_log_file = log_file or _default_log_file()
    resolved_log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = _ApplicationFileHandler(resolved_log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return resolved_log_file


def _default_log_file() -> Path:
    state_home = os.getenv("XDG_STATE_HOME")
    base_directory = (
        Path(state_home).expanduser()
        if state_home
        else Path.home() / ".local" / "state"
    )
    return base_directory / "strava-analysis" / "application.log"
