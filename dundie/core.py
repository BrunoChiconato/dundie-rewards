"""Core module of dundie"""
import os
import sys
from csv import reader
from typing import Any, Dict, List

from sqlmodel import select

from dundie.database import get_session
from dundie.models import Person
from dundie.settings import DATEFMT
from dundie.utils.db import add_movement, add_person
from dundie.utils.decorator import require_auth
from dundie.utils.exchange import get_rates
from dundie.utils.log import get_logger

log = get_logger()
Query = Dict[str, Any]
ResultDict = List[Dict[str, Any]]


@require_auth
def load(filepath: str, from_person: Person) -> list:
    """Loads data from filepath to a SQLite database.

    Args:
        filepath (str): Path to the CSV file.
        from_person (Person): Person instance.

    Returns:
        list: List of dictionaries with the added data.

    Raises:
        RuntimeError: If the person is not a manager.
        FileNotFoundError: If the file does not exist.
    """
    try:
        if from_person.role != "Manager":
            raise RuntimeError(
                "You need to be a manager to perform this action."
            )
        else:
            try:
                csv_data = reader(open(filepath))
            except FileNotFoundError as e:
                log.error(str(e))
                raise e

            people = []
            headers = ["name", "dept", "role", "email", "currency"]

            with get_session() as session:
                for line in csv_data:
                    person_data = dict(
                        zip(headers, [item.strip() for item in line])
                    )
                    instance = Person(**person_data)
                    person, created = add_person(session, instance)
                    return_data = person.dict(exclude={"id"})
                    return_data["created"] = created
                    people.append(return_data)

                session.commit()

            return people
    except Exception as e:
        print(str(e))
        sys.exit(1)


@require_auth
def read(from_person: Person, **query: Query) -> ResultDict:
    """Read data from the database and filters using query.

    Args:
        from_person (Person): Person instance.
        query (Dict): Query parameters.

    Returns:
        ResultDict: List of dictionaries with the data.

    Raises:
        RuntimeError: If the person is not a manager.
    """
    query = {k: v for k, v in query.items() if v is not None}
    return_data = []

    query_statements = []
    try:
        if "dept" in query and from_person.role == "Manager":
            query_statements.append(Person.dept == query["dept"])
        elif "dept" in query and from_person.role != "Manager":
            raise RuntimeError(
                "You need to be a manager to perform this action."
            )

        if "email" in query and from_person.role == "Manager":
            query_statements.append(Person.email == query["email"])
        elif "email" in query and from_person.email != query["email"]:
            raise RuntimeError(
                "You need to be a manager to perform this action."
            )
    except Exception as e:
        print(str(e))
        sys.exit(1)

    sql = select(Person)
    if query_statements or from_person.role == "Manager":
        sql = sql.where(*query_statements)
    elif query_statements or from_person.role != "Manager":
        sql = sql.where(Person.email == from_person.email)

    with get_session() as session:
        currencies = session.exec(
            select(Person.currency).distinct(Person.currency)
        )
        rates = get_rates(currencies)
        results = session.exec(sql)
        for person in results:
            total = rates[person.currency].values * person.balance[0].value
            return_data.append(
                {
                    "email": person.email,
                    "balance": person.balance[0].value,
                    "last_movement": person.movement[-1].date.strftime(
                        DATEFMT
                    ),
                    **person.dict(exclude={"id"}),
                    **{"value": total},
                }
            )

    return return_data, from_person.role


def add(value: int, **query: Query) -> None:
    """Add value to each record on query.

    Args:
        value (int): Value to add.
        query (Dict): Query parameters.

    Returns:
        None: If no results are found.

    Raises:
        RuntimeError: If the person is not a manager.
    """
    people, auth_role = read(**query)

    try:
        if auth_role != "Manager":
            raise RuntimeError(
                "You need to be a manager to perform this action."
            )
        else:
            query = {k: v for k, v in query.items() if v is not None}

            if not people:
                raise RuntimeError("No results found.")

            with get_session() as session:
                user = os.getenv("USER")
                for person in people:
                    instance = session.exec(
                        select(Person).where(Person.email == person["email"])
                    ).first()
                    add_movement(session, instance, value, user)

                session.commit()
    except Exception as e:
        print(str(e))
        sys.exit(1)


@require_auth
def transfer(value: int, to: str, from_person: Person) -> None:
    """Transfer points from one employee to another.

    Args:
        value (int): Value to transfer.
        to (str): Email of the destination employee.
        from_person (Person): Person instance.

    Returns:
        None: If no results are found.

    Raises:
        RuntimeError: If the person is not a manager.
        RuntimeError: If the origin employee does not have enough balance.
        RuntimeError: If the origin employee is the same as the destination employee.
    """
    from_balance = from_person.balance[0].value
    from_email = from_person.email

    try:
        if from_balance < value:
            raise RuntimeError("Insufficient balance.")

        if from_email == to:
            raise RuntimeError("You cannot transfer to yourself.")

        with get_session() as session:
            user = os.getenv("USER")

            from_instance = session.exec(
                select(Person).where(Person.email == from_email)
            ).first()
            if not from_instance:
                raise RuntimeError(
                    f"Origin employee ({from_email}) not found."
                )

            add_movement(session, from_instance, -value, user)

            user = os.getenv("USER")
            to_instance = session.exec(
                select(Person).where(Person.email == to)
            ).first()
            if not to_instance:
                raise RuntimeError(f"Destination employee ({to}) not found.")

            add_movement(session, to_instance, value, user)

            session.commit()
    except Exception as e:
        print(str(e))
        sys.exit(1)


@require_auth
def movements(from_person: Person) -> ResultDict:
    """Get movements from a employee.

    Args:
        from_person (Person): Person instance.

    Returns:
        ResultDict: List of dictionaries with the data.
    """
    return_data = []

    sql = select(Person)
    sql = sql.where(Person.email == from_person.email)

    with get_session() as session:
        results = session.exec(sql)
        for person in results:
            for movement in reversed(person.movement):
                return_data.append(
                    {
                        "date": movement.date.strftime(DATEFMT),
                        "value": movement.value,
                        "actor": movement.actor,
                    }
                )

    return return_data
