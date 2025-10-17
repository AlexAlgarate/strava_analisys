import logging

FORMAT_LOGGING = (
    "%(levelname)s -- %(asctime)s -- %(name)s -- %(funcName)s : %(message)s"
)
DATEFMT_LOGGING = "%y-%m-%d %H:%M:%S"


def setup_logging(level: int = logging.INFO) -> None:
    # Configure the root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Create formatters
    formatter = logging.Formatter(fmt=FORMAT_LOGGING, datefmt=DATEFMT_LOGGING)
    
    # Create and configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Create and configure file handler
    file_handler = logging.FileHandler('logs.txt')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
