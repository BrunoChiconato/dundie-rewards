"""Core module of dundie"""

import os
from csv import reader

from dundie.database import add_movement, add_person, commit, connect
from dundie.utils.log import get_logger

log = get_logger()


def load(filepath):
    """Loads data from filepath to a databse."""
    try:
        csv_data = reader(open(filepath))
    except FileNotFoundError as e:
        log.error(str(e))
        raise e

    db = connect()
    people = []
    headers = ["name", "department", "role", "e-mail"]
    for line in csv_data:
        person_data = dict(zip(headers, [line.strip() for line in line]))
        pk = person_data.pop("e-mail")
        person, created = add_person(db, pk, person_data)

        return_data = person.copy()
        return_data["created"] = created
        return_data["e-mail"] = pk
        people.append(return_data)

    commit(db)
    return people


def read(dept=None, email=None):
    db = connect()
    results = []
    for pk, person in db["people"].items():
        item = {
            "e-mail": pk,
            "dept": person.get("department"),
            "role": person.get("role"),
            "name": person.get("name"),
            "balance": db["balance"].get(pk, 0),
            "last_movement": (
                db["movement"][pk][-1]["date"]
                if pk in db["movement"] and db["movement"][pk]
                else None
            ),
        }
        if dept and item["dept"] != dept:
            continue
        if email and item["e-mail"] != email:
            continue
        results.append(item)
    return results


def add(value, **query):
    """Add value to each record on query."""
    people = read(**query)
    if not people:
        raise RuntimeError("No records found.")

    db = connect()
    user = os.getenv("USER")
    for person in people:
        add_movement(db, person["e-mail"], value, user)
    commit(db)
