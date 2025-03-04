"""Logging utility module."""

import logging
import os
from logging import handlers

LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING").upper()
log = logging.getLogger("dundie")
fmt = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s l:%(lineno)d - f:%(filename)s: %(message)s"
)


def get_logger(logfile="dundie.log") -> logging.Logger:
    """Returns a logger object.

    Args:
        logfile (str): Log file name.

    Returns:
        logging.Logger: Logger object.
    """
    fh = handlers.RotatingFileHandler(
        logfile,
        maxBytes=300,
        backupCount=10,
    )
    fh.setLevel(LOG_LEVEL)
    fh.setFormatter(fmt)
    log.addHandler(fh)
    return log
