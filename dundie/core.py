"""Core module for the Dundie Rewards System.

This module implements the core functionality for managing employee data and point
transactions in the Dundie Rewards System. The operations include loading employee data
from CSV files, retrieving employee records, adding or removing points, transferring points
between employees, and retrieving transaction movements. All operations require proper
authentication.
"""

import sys
from csv import reader
from typing import Any, Dict, List

from sqlmodel import select

from dundie.database import get_session
from dundie.models import Person
from dundie.settings import DATEFMT
from dundie.utils.auth import requires_auth
from dundie.utils.db import add_movement, add_person
from dundie.utils.exchange import get_rates
from dundie.utils.log import get_logger
from dundie.utils.auth import AuthenticationError

log = get_logger()
Query = Dict[str, Any]
ResultDict = List[Dict[str, Any]]

# TODO: Modify prints to logging
# TODO: Review add function


@requires_auth
def load(filepath: str, from_person: Person) -> ResultDict:
    """Load employee data from a CSV file into the database.

    This function reads a CSV file from the given filepath, validates and parses its content,
    and loads the employee data into the database. Each row in the CSV file is expected to contain
    the following columns: 'name', 'dept', 'role', 'email', and 'currency'. For every row,
    a new Person instance is created and added to the database, along with a record indicating
    whether the entry was newly created.

    Args:
        filepath (str): The path to the CSV file containing employee data.
        from_person (Person): The authenticated user performing this operation. Must be a superuser.

    Returns:
        ResultDict: A list of dictionaries representing the loaded employee records, each including
            a 'created' key to indicate creation status.

    Raises:
        AuthenticationError: If the authenticated user is not authorized to perform this action.
        FileNotFoundError: If the specified CSV file is not found.
        SystemExit: If any other error occurs during the loading process.
    """
    try:
        if from_person is None or from_person.superuser:
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
        else:
            raise AuthenticationError("You can not perform this action!")
    except Exception as e:
        print(str(e))
        sys.exit(1)


@requires_auth
def read(from_person: Person, **query: Query) -> ResultDict:
    """Retrieve employee records from the database based on provided filters.

    This function constructs a database query using optional filter parameters (such as department
    and email). Managers can filter by both 'dept' and 'email', whereas non-superusers are limited to
    viewing only their own record. Additionally, the function calculates a converted value for each
    employee based on current exchange rates.

    Args:
        from_person (Person): The authenticated user performing the query.
        **query (Query): Optional keyword arguments to filter the query (e.g., 'dept' or 'email').

    Returns:
        ResultDict: A list of dictionaries containing employee data along with calculated balance values.

    Raises:
        RuntimeError: If a non-superuser attempts to filter by department or email.
        SystemExit: If an error occurs during the query execution.
    """
    query = {k: v for k, v in query.items() if v is not None}
    return_data = []

    query_statements = []
    try:
        if "dept" in query and from_person.superuser:
            query_statements.append(Person.dept == query["dept"])
        elif "dept" in query and not from_person.superuser:
            raise RuntimeError("You can not perform this action!")

        if "email" in query and from_person.superuser:
            query_statements.append(Person.email == query["email"])
        elif "email" in query and not from_person.superuser:
            raise RuntimeError("You can not perform this action!")
        elif not from_person.superuser:
            query_statements.append(Person.email == from_person.email)

        sql = select(Person)
        if query_statements:
            sql = sql.where(*query_statements)

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
                        "last movement": person.movement[-1].date.strftime(
                            DATEFMT
                        ),
                        **person.dict(exclude={"id"}),
                        **{"value": total},
                    }
                )

        return return_data

    except Exception as e:
        print(str(e))
        sys.exit(1)


@requires_auth
def add(value: int, from_person: Person, **query: Query) -> None:
    """Add points to selected employee records.

    This function adds a specified number of points to every employee record that matches the given
    filters. For non-superusers, the total points to be added must not exceed the authenticated user's
    available balance. A corresponding movement record is created for each transaction.

    Args:
        value (int): The number of points to add.
        from_person (Person): The authenticated user initiating the addition.
        **query (Query): Optional filters (e.g., 'dept' or 'email') to select target employees.

    Returns:
        None

    Raises:
        RuntimeError: If no matching records are found or if the authenticated user's balance is insufficient.
        SystemExit: If an error occurs during the addition process.
    """
    query = {k: v for k, v in query.items() if v is not None}
    people = read(**query)

    try:
        if not people:
            raise RuntimeError("Not Found")

        total = len(people) * value
        if from_person.balance[0].value < total and not from_person.superuser:
            raise RuntimeError(f"Not enough balance to transfer {total}")

        with get_session() as session:
            for person in people:
                instance = session.exec(
                    select(Person).where(Person.email == person["email"])
                ).first()
                add_movement(session, instance, value, from_person.email)

                if not from_person.superuser:
                    from_instance = session.exec(
                        select(Person).where(Person.email == from_person.email)
                    ).first()
                    add_movement(
                        session,
                        from_instance,
                        -abs(value),
                        person["email"],
                    )

            session.commit()

    except Exception as e:
        print(str(e))
        sys.exit(1)


@requires_auth
def transfer(value: int, to_person: str, from_person: Person) -> None:
    """Transfer points from the authenticated user's account to another employee.

    This function transfers a specified number of points from the authenticated user's account to
    the account of the employee identified by the given email address. It ensures that the sender
    has sufficient points and that the transfer is not made to the sender's own account. A movement
    record is created for both the sender and the recipient.

    Args:
        value (int): The number of points to transfer.
        to_person (str): The email address of the recipient employee.
        from_person (Person): The authenticated user initiating the transfer.

    Returns:
        None

    Raises:
        ValueError: If the authenticated user does not have enough balance or if attempting to transfer
            points to themselves.
        RuntimeError: If the recipient's email is not found in the database.
        SystemExit: If an error occurs during the transfer process.
    """
    try:
        if value > from_person.balance[0].value:
            raise ValueError("You don't have enough balance!")

        if to_person == from_person.email:
            raise ValueError("You can't transfer points to yourself!")

        with get_session() as session:
            person = session.exec(
                select(Person).where(Person.email == to_person)
            ).first()

        if person is None:
            raise RuntimeError(f"Email '{to_person}' not found!")

        with get_session() as session:
            add_instance = session.exec(
                select(Person).where(Person.email == to_person)
            ).first()
            add_movement(session, add_instance, value, from_person.email)

            to_person_name = add_instance.name

            remove_instance = session.exec(
                select(Person).where(Person.email == from_person.email)
            ).first()
            add_movement(
                session, remove_instance, -abs(value), from_person.email
            )

            session.commit()

        print(
            f"Success! You have transfered {value} points from your balance "
            f"to {to_person_name}."
        )

    except Exception as e:
        print(str(e))
        sys.exit(1)


@requires_auth
def movements(from_person: Person) -> ResultDict:
    """Retrieve transaction movements from the database.

    This function fetches the transaction history for the authenticated user. Managers receive
    the complete history for all employees, while non-superusers only obtain their own transaction
    records. For each transaction, a converted movement value is calculated using the current exchange
    rates. The results are then sorted by date in descending order.

    Args:
        from_person (Person): The authenticated user whose transaction history is to be retrieved.

    Returns:
        ResultDict: A list of dictionaries representing the transaction movements. Each dictionary contains:
            - 'Name': Employee's name.
            - 'Date': The date of the transaction.
            - 'Movement': The original movement value.
            - 'Converted Movement': The movement value converted based on the current exchange rate.
            - 'Actor': The identifier of the transaction initiator.
    """
    return_data = []

    query_statements = []

    if not from_person.superuser:
        query_statements.append(Person.email == from_person.email)

    sql = select(Person)
    if query_statements:
        sql = sql.where(*query_statements)

    with get_session() as session:
        currencies = session.exec(
            select(Person.currency).distinct(Person.currency)
        )
        rates = get_rates(currencies)
        results = session.exec(sql)
        for person in results:
            for movement in person.movement:
                total = rates[person.currency].values * movement.value
                return_data.append(
                    {
                        "Name": person.name,
                        "Date": movement.date.strftime(DATEFMT),
                        "Movement": movement.value,
                        "Converted Movement": total,
                        "Actor": movement.actor,
                    }
                )
    return_data = sorted(return_data, key=lambda x: x["Date"], reverse=True)

    return return_data
