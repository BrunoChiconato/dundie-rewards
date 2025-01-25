"""Core module of dundie"""

from csv import reader

from dundie.database import add_person, commit, connect
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
