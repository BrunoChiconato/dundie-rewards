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
    """Loads data from filepath to a database."""
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
    """Read data from the database and filters using query."""
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

    return return_data


@require_auth
def add(value: int, from_person: Person, **query: Query):
    """Add value to each record on query."""
    try:
        if from_person.role != "Manager":
            raise RuntimeError(
                "You need to be a manager to perform this action."
            )
        else:
            query = {k: v for k, v in query.items() if v is not None}
            people = read(**query)

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
