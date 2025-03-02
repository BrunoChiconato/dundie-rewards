"""Email utilities."""

import re

from dundie.utils.log import get_logger

log = get_logger()

regex = r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"


def check_valid_email(address: str) -> bool:
    """Check if email is valid.

    Args:
        address (str): Email address.

    Returns:
        bool: True or False if the emails is a valid one.
    """
    return bool(re.fullmatch(regex, address))
