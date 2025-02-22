"""User utilities."""

from random import sample
from string import ascii_letters, digits

from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()


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


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
