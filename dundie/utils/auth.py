"""Module to define decorators for the CLI commands."""

import os
from functools import wraps

from sqlalchemy.orm import selectinload
from sqlmodel import select

from dundie.database import get_session
from dundie.models import Person


class AuthenticationError(Exception):
    """Exception raised for authentication errors."""

    pass


def requires_auth(func):
    """Decorator to require authentication.

    Args:
        func (function): Function to decorate.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        email = os.getenv("DUNDIE_EMAIL")
        password = os.getenv("DUNDIE_PASSWORD")

        if not all([email, password]):
            raise AuthenticationError(
                "Variables DUNDIE_EMAIL and DUNDIE_PASSWORD not definied."
            )

        with get_session() as session:
            person = session.exec(
                select(Person)
                .options(
                    selectinload(Person.balance),
                    selectinload(Person.user),
                    selectinload(Person.movement),
                )
                .where(Person.email == email)
            ).first()

            if not person:
                raise AuthenticationError("User doesn't exist.")
            # TODO: Encrypt the password
            if person.user.password != password:
                raise AuthenticationError("Authentication Error.")

        return func(*args, from_person=person, **kwargs)

    return wrapper
