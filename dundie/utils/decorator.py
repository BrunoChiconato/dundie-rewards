import sys
from functools import wraps

from sqlalchemy.orm import selectinload  # type: ignore
from sqlmodel import select  # type: ignore

from dundie.database import get_session
from dundie.models import Person, User


class AuthenticationError(Exception):
    pass


def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            input_email = input("Enter your email: ").strip()
            input_password = input("Enter your password: ").strip()

            if not input_email or not input_password:
                raise AuthenticationError("Email or password cannot be empty!")

            with get_session() as session:
                person = session.exec(
                    select(Person)
                    .options(
                        selectinload(Person.balance),
                        selectinload(Person.user),
                        selectinload(Person.movement),
                    )
                    .where(Person.email == input_email)
                ).first()

            if not person:
                raise AuthenticationError("User doesn't exist!")

            if person.user.password != input_password:
                raise AuthenticationError("Wrong password!")

            return func(*args, from_person=person, **kwargs)

        except AuthenticationError as e:
            print(str(e))
            sys.exit(1)

    return wrapper
