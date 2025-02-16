"""Database utilities."""
from typing import Optional

from sqlmodel import Session, select

from dundie.models import Balance, Movement, Person, User
from dundie.settings import EMAIL_FROM
from dundie.utils.email import send_email


def add_person(session: Session, instance: Person) -> tuple[Person, bool]:
    """Add person to database.

    - Email is unique (resolved by dictionary hash table).
    - If exists, update, ele create.
    - Set initial balance (managers = 100, others = 500).
    - Generate a password if user is new and send email.

    Args:
        session (Session): Database session.
        instance (Person): Person instance.

    Returns:
        tuple[Person, bool]: Person instance and created flag.
    """
    existing = session.exec(
        select(Person).where(Person.email == instance.email)
    ).first()

    created = existing is None
    if created:
        session.add(instance)
        set_initial_balance(session, instance)
        password = set_initial_password(session, instance)
        # TODO: Usar sistema de filas para envio de email
        send_email(EMAIL_FROM, instance.email, "Your password", password)

        return instance, created
    else:
        existing.dept = instance.dept
        existing.role = instance.role
        existing.currency = instance.currency
        session.add(existing)
        return instance, created


def set_initial_password(session: Session, instance: Person) -> str:
    """Generate and saves a simple password.
    
    Args:
        session (Session): Database session.
        instance (Person): Person instance.
    
    Returns:
        str: Generated password.
    """
    user = User(person=instance)
    session.add(user)
    return user.password


def set_initial_balance(session: Session, person: Person):
    """Add movement and set initial balance.
    
    Args:
        session (Session): Database session.
        person (Person): Person instance.
    """
    value = 100 if person.role == "Manager" else 500
    add_movement(session, person, value)


def add_movement(
    session: Session,
    person: Person,
    value: int,
    actor: Optional[str] = "system",
):
    """Add movement to balance.

    Args:
        session (Session): Database session.
        person (Person): Person instance.
        value (int): Value to add.
        actor (str, optional): Actor who added the movement. Defaults to "system".
    """
    movement = Movement(person=person, value=value, actor=actor)
    session.add(movement)

    movements = session.exec(select(Movement).where(Movement.person == person))

    total = sum([mov.value for mov in movements])

    existing_balance = session.exec(
        select(Balance).where(Balance.person == person)
    ).first()

    if existing_balance:
        existing_balance.value = total
        session.add(existing_balance)
    else:
        session.add(Balance(person=person, value=total))
