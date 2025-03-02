import pytest

from dundie.core import load, read
from dundie.database import get_session
from dundie.models import Person
from dundie.utils.db import add_person

from .constants import PEOPLE_FILE


@pytest.mark.unit
def test_read_with_query(monkeypatch):
    session = get_session()

    monkeypatch.setenv("DUNDIE_EMAIL", "joe@doe.com")
    monkeypatch.setenv("DUNDIE_PASSWORD", "123456")

    data = {
        "role": "Salesman",
        "dept": "Sales",
        "name": "Joe Doe",
        "email": "joe@doe.com",
    }
    _, created = add_person(session, Person(**data), "123456")
    assert created is True

    monkeypatch.setenv("DUNDIE_EMAIL", "jim@doe.com")
    monkeypatch.setenv("DUNDIE_PASSWORD", "123456")

    data = {
        "role": "Manager",
        "dept": "Management",
        "name": "Jim Doe",
        "email": "jim@doe.com",
    }
    _, created = add_person(session, Person(**data), "123456")
    assert created is True

    session.commit()

    response = read()
    assert len(response) == 2

    response = read(dept="Management")
    assert len(response) == 1
    assert response[0]["name"] == "Jim Doe"

    response = read(email="joe@doe.com")
    assert len(response) == 1
    assert response[0]["name"] == "Joe Doe"


@pytest.mark.unit
def test_read_all_data(monkeypatch):
    monkeypatch.setenv("DUNDIE_EMAIL", "schrute@dundiermifflin.com")
    monkeypatch.setenv("DUNDIE_PASSWORD", "123456")
    monkeypatch.setattr("dundie.utils.auth.verify_password", lambda x, y: True)

    load(PEOPLE_FILE)
    result = read()
    assert len(result) == 3


@pytest.mark.unit
def test_read_only_one_dept(monkeypatch):
    monkeypatch.setenv("DUNDIE_EMAIL", "schrute@dundiermifflin.com")
    monkeypatch.setenv("DUNDIE_PASSWORD", "123456")
    monkeypatch.setattr("dundie.utils.auth.verify_password", lambda x, y: True)

    load(PEOPLE_FILE)
    result = read(dept="Sales")
    assert len(result) == 2


@pytest.mark.unit
def test_read_only_one_person(monkeypatch):
    monkeypatch.setenv("DUNDIE_EMAIL", "schrute@dundiermifflin.com")
    monkeypatch.setenv("DUNDIE_PASSWORD", "123456")
    monkeypatch.setattr("dundie.utils.auth.verify_password", lambda x, y: True)

    load(PEOPLE_FILE)
    result = read(email="jim@dundiermifflin.com")
    assert len(result) == 1


@pytest.mark.unit
def test_not_authorized_read_dept_command(monkeypatch):
    with get_session() as session:
        unauthorized_data = {
            "name": "Jim Doe",
            "dept": "Sales",
            "role": "Salesman",
            "email": "jim@doe.com",
            "currency": "USD",
        }
        password = "1234"
        unauthorized_person, _ = add_person(
            session, Person(**unauthorized_data), password
        )

        monkeypatch.setenv("DUNDIE_EMAIL", unauthorized_person.email)
        monkeypatch.setenv("DUNDIE_PASSWORD", password)

        session.commit()

    query = {"dept": "Sales"}

    with pytest.raises(RuntimeError) as exc_info:
        read(**query)

    assert "You can not perform this action!" in str(exc_info.value)


@pytest.mark.unit
def test_not_authorized_read_email_command(monkeypatch):
    with get_session() as session:
        unauthorized_data = {
            "name": "Jim Doe",
            "dept": "Sales",
            "role": "Salesman",
            "email": "jim@doe.com",
            "currency": "USD",
        }
        password = "1234"
        unauthorized_person, _ = add_person(
            session, Person(**unauthorized_data), password
        )

        monkeypatch.setenv("DUNDIE_EMAIL", unauthorized_person.email)
        monkeypatch.setenv("DUNDIE_PASSWORD", password)

        session.commit()

    query = {"email": "test@test.com"}

    with pytest.raises(RuntimeError) as exc_info:
        read(**query)

    assert "You can not perform this action!" in str(exc_info.value)


@pytest.mark.unit
def test_employee_read_command(monkeypatch):
    with get_session() as session:
        unauthorized_data = {
            "name": "Jim Doe",
            "dept": "Sales",
            "role": "Salesman",
            "email": "jim@doe.com",
            "currency": "USD",
        }
        password = "1234"
        unauthorized_person, _ = add_person(
            session, Person(**unauthorized_data), password
        )

        monkeypatch.setenv("DUNDIE_EMAIL", unauthorized_person.email)
        monkeypatch.setenv("DUNDIE_PASSWORD", password)

        session.commit()

        query = {}
        read(**query)

        assert unauthorized_person.superuser is False
