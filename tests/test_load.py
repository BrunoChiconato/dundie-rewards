import pytest

from dundie.core import load, add_person
from dundie.database import get_session
from dundie.models import Person
from dundie.utils.auth import AuthenticationError

from .constants import PEOPLE_FILE


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
@pytest.mark.high
def test_load_positive_has_2_people():
    """Test function load function."""
    assert len(load(PEOPLE_FILE)) == 3


@pytest.mark.unit
@pytest.mark.high
def test_load_positive_first_name_starts_with_j():
    """Test function load function."""
    assert load(PEOPLE_FILE)[0]["name"] == "Jim Halpert"


@pytest.mark.unit
@pytest.mark.high
def test_negative_filenotfound():
    """Test function load function."""
    with pytest.raises(FileNotFoundError):
        load("assets/invalid.csv")


@pytest.mark.unit
def test_not_authorized_load_command(monkeypatch):
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

    with pytest.raises(AuthenticationError) as exc_info:
        load(PEOPLE_FILE)

    assert "You can not perform this action!" in str(exc_info.value)
