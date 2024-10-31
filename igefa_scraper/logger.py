import logging


def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    Sets up a logger with the specified name and log file.

    Args:
        name (str): Name of the logger.
        log_file (str): File to write logs to.
        level (int): Logging level.

    Returns:
        logging.Logger: Configured logger.
    """
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(stream_handler)

    # Prevent log propagation to the root logger
    logger.propagate = False

    return logger


# Initialize the main logger
main_logger = setup_logger("main_logger", "scraper.log")
