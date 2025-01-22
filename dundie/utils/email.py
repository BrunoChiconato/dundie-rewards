import re

regex = r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"


def check_valid_email(adress):
    """Check if email is valid."""
    return bool(re.fullmatch(regex, adress))
