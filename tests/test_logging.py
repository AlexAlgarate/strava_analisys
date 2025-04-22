import logging
from unittest.mock import patch

from src.utils.logging import Logger


class TestLogger:
    def test_setup_logger(self):
        logger = Logger().setup_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.getEffectiveLevel() == logging.INFO

    @patch("logging.basicConfig")
    def test_logger_configuration(self, mock_basic_config):
        Logger().setup_logger()
        mock_basic_config.assert_called_once_with(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
