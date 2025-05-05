import logging

FORMAT_LOGGING = (
    "%(levelname)s -- %(asctime)s -- %(name)s -- %(funcName)s : %(message)s"
)
DATEFMT_LOGGING = "%y-%m-%d %H:%M:%S"


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format=FORMAT_LOGGING,
        datefmt=DATEFMT_LOGGING,
    )
