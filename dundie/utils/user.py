"""User utilities."""

from random import sample
from string import ascii_letters, digits


def generate_simple_password(size=8) -> str:
    """Generate a simple password.
    [A-Z][a-z][0-9]

    Args:
        size (int): Password size.

    Returns:
        str: Generated password.
    """
    password = sample(ascii_letters + digits, size)
    return "".join(password)
