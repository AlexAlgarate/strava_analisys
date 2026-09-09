import logging
from collections.abc import Iterator
from pathlib import Path

import pytest

from src.utils.logger_config import setup_logging


@pytest.fixture
def isolated_root_logger() -> Iterator[logging.Logger]:
    root_logger = logging.getLogger()
    previous_handlers = root_logger.handlers[:]
    previous_level = root_logger.level
    for handler in previous_handlers:
        root_logger.removeHandler(handler)

    yield root_logger

    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)
    for handler in previous_handlers:
        root_logger.addHandler(handler)
    root_logger.setLevel(previous_level)


def test_setup_logging_writes_to_console_and_explicit_file(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    isolated_root_logger: logging.Logger,
) -> None:
    log_file = tmp_path / "logs" / "application.log"

    result = setup_logging(logging.WARNING, log_file=log_file)
    logging.getLogger("strava-test").warning("training complete")
    for handler in isolated_root_logger.handlers:
        handler.flush()

    assert result == log_file
    assert isolated_root_logger.level == logging.WARNING
    assert _application_handler_count(isolated_root_logger) == 2
    assert "training complete" in capsys.readouterr().err
    assert "training complete" in log_file.read_text(encoding="utf-8")


def test_setup_logging_is_idempotent(
    tmp_path: Path,
    isolated_root_logger: logging.Logger,
) -> None:
    log_file = tmp_path / "application.log"

    setup_logging(log_file=log_file)
    setup_logging(logging.DEBUG, log_file=log_file)

    assert _application_handler_count(isolated_root_logger) == 2
    assert isolated_root_logger.level == logging.DEBUG


def test_default_log_path_uses_xdg_state_home(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    isolated_root_logger: logging.Logger,
) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))

    result = setup_logging()

    assert result == tmp_path / "strava-analysis" / "application.log"
    assert result.exists()


def _application_handler_count(logger: logging.Logger) -> int:
    return sum(
        handler.__class__.__name__.startswith("_Application")
        for handler in logger.handlers
    )
