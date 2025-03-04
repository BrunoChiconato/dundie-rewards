import pytest
from sqlmodel import select

from dundie.database import get_session
from dundie.models import InvalidEmailError, Person
from dundie.utils.db import add_movement, add_person


@pytest.fixture(scope="function", autouse=True)
def auth(monkeypatch):
    with get_session() as session, monkeypatch.context() as ctx:
        data = {
            "role": "Manager",
            "dept": "Management",
            "name": "Michael Scott",
            "email": "scott@dm.com",
        }
        password = "1234"
        person, _ = add_person(session, Person(**data), password)
        ctx.setenv("DUNDIE_EMAIL", person.email)
        ctx.setenv("DUNDIE_PASSWORD", password)
        session.commit()
        yield


@pytest.mark.unit
def test_ensure_database_is_test():
    session = get_session()
    assert "test.db" in session.get_bind().engine.url.database


@pytest.mark.unit
def test_commit_to_database():
    session = get_session()
    data = {
        "name": "Joe Doe",
        "role": "Salesman",
        "dept": "Sales",
        "email": "joe@doe.com",
    }
    session.add(Person(**data))
    session.commit()

    assert (
        session.exec(select(Person).where(Person.email == data["email"]))
        .first()
        .email
        == data["email"]
    )


@pytest.mark.unit
def test_add_person_for_the_first_time():
    data = {
        "role": "Salesman",
        "dept": "Sales",
        "name": "Joe Doe",
        "email": "joe@doe.com",
    }
    session = get_session()
    person, created = add_person(session, Person(**data))
    assert created is True
    session.commit()
    session.refresh(person)

    assert person.email == data["email"]
    assert person.balance[0].value == 500
    assert len(person.movement) > 0
    assert person.movement[0].value == 500


@pytest.mark.unit
def test_negative_add_person_invalid_email():
    data = {
        "role": "Salesman",
        "dept": "Sales",
        "name": "Joe Doe",
        "email": ".@bla",
    }
    session = get_session()
    with pytest.raises(InvalidEmailError):
        add_person(session, Person.model_validate(data))


@pytest.mark.unit
def test_add_or_remove_points_for_person():
    data = {
        "role": "Salesman",
        "dept": "Sales",
        "name": "Joe Doe",
        "email": "joe@doe.com",
    }
    session = get_session()
    person, created = add_person(session, Person(**data))
    assert created is True
    session.commit()

    session.refresh(person)
    before = person.balance[0].value

    add_movement(session, person, -100, "manager")
    session.commit()

    session.refresh(person)
    after = person.balance[0].value

    assert after == before - 100
    assert after == 400
    assert before == 500


@pytest.mark.unit
def test_update_existing_user():
    initial_data = {
        "role": "Salesman",
        "dept": "Sales",
        "name": "Joe Doe",
        "email": "joe@doe.com",
        "currency": "USD",
    }
    session = get_session()
    _, created = add_person(session, Person(**initial_data))
    session.commit()

    assert created is True

    updated_data = {
        "role": "Manager",
        "dept": "Marketing",
        "name": "Joe Doe",
        "email": "joe@doe.com",
        "currency": "EUR",
    }

    _, created = add_person(session, Person(**updated_data))
    session.commit()

    assert created is False

    person_db = session.exec(
        select(Person).where(Person.email == "joe@doe.com")
    ).first()
    assert person_db.dept == "Marketing"
    assert person_db.role == "Manager"
    assert person_db.currency == "EUR"
