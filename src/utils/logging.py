import logging

FORMAT_LOGGING = "%(asctime)s - %(levelname)s - %(message)s"
DATEFMT_LOGGING = "%Y-%m-%d %H:%M:%S"


class Logger:
    @staticmethod
    def setup_logger():
        logging.basicConfig(
            level=logging.INFO,
            format=FORMAT_LOGGING,
            datefmt=DATEFMT_LOGGING,
        )
        return logging.getLogger(__name__)
