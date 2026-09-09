import logging
from pathlib import Path

import pytest

from src.utils.logger_config import setup_logging


def test_setup_logging_writes_to_console_and_file(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root_logger = logging.getLogger()
    previous_handlers = root_logger.handlers[:]
    previous_level = root_logger.level
    for handler in previous_handlers:
        root_logger.removeHandler(handler)
    monkeypatch.chdir(tmp_path)

    try:
        setup_logging(logging.WARNING)
        logging.getLogger("strava-test").warning("training complete")
        for handler in root_logger.handlers:
            handler.flush()

        assert root_logger.level == logging.WARNING
        assert len(root_logger.handlers) == 2
        assert "training complete" in capsys.readouterr().err
        assert "training complete" in (tmp_path / "logs.txt").read_text()
    finally:
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)
        for handler in previous_handlers:
            root_logger.addHandler(handler)
        root_logger.setLevel(previous_level)
