import logging

FORMAT_LOGGING = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
DATEFMT_LOGGING = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format=FORMAT_LOGGING,
        datefmt=DATEFMT_LOGGING,
    )
