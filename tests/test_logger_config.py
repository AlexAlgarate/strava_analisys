import logging
import os
import stat
from collections.abc import Iterator
from pathlib import Path

import pytest

from src.infrastructure.logging import setup_logging


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


def test_setup_logging_creates_private_directory_and_file_under_open_umask(
    tmp_path: Path,
    isolated_root_logger: logging.Logger,
) -> None:
    log_file = tmp_path / "private-logs" / "application.log"
    previous_umask = os.umask(0)
    try:
        setup_logging(log_file=log_file)
    finally:
        os.umask(previous_umask)

    assert stat.S_IMODE(log_file.parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(log_file.stat().st_mode) == 0o600


def test_setup_logging_restricts_existing_log_file(
    tmp_path: Path,
    isolated_root_logger: logging.Logger,
) -> None:
    log_file = tmp_path / "application.log"
    log_file.write_text("existing\n", encoding="utf-8")
    log_file.chmod(0o666)

    setup_logging(log_file=log_file)

    assert stat.S_IMODE(log_file.stat().st_mode) == 0o600


def test_default_log_directory_is_restricted_when_it_already_exists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    isolated_root_logger: logging.Logger,
) -> None:
    log_directory = tmp_path / "strava-analysis"
    log_directory.mkdir(mode=0o777)
    log_directory.chmod(0o777)
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))

    log_file = setup_logging()

    assert stat.S_IMODE(log_directory.stat().st_mode) == 0o700
    assert stat.S_IMODE(log_file.stat().st_mode) == 0o600


def test_setup_logging_refuses_symbolic_link_file(
    tmp_path: Path,
    isolated_root_logger: logging.Logger,
) -> None:
    target = tmp_path / "target.log"
    target.write_text("do not append\n", encoding="utf-8")
    log_file = tmp_path / "application.log"
    log_file.symlink_to(target)

    with pytest.raises(OSError):
        setup_logging(log_file=log_file)

    assert target.read_text(encoding="utf-8") == "do not append\n"


def test_setup_logging_refuses_symbolic_link_directory(
    tmp_path: Path,
    isolated_root_logger: logging.Logger,
) -> None:
    target_directory = tmp_path / "target"
    target_directory.mkdir()
    log_directory = tmp_path / "logs"
    log_directory.symlink_to(target_directory, target_is_directory=True)

    with pytest.raises(OSError):
        setup_logging(log_file=log_directory / "application.log")

    assert list(target_directory.iterdir()) == []


def _application_handler_count(logger: logging.Logger) -> int:
    return sum(
        handler.__class__.__name__.startswith("_Application")
        for handler in logger.handlers
    )
