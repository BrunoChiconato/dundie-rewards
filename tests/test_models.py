import pytest
import dundie.utils.email
from dundie.models import InvalidEmailError, Person


@pytest.mark.unit
def test_valid_email(monkeypatch):
    monkeypatch.setattr(
        "dundie.utils.email.check_valid_email", lambda email: True
    )

    person = Person(
        email="joe@doe.com",
        name="John Doe",
        dept="Engineering",
        role="Developer",
        currency="USD",
    )

    assert person.email == "joe@doe.com"


@pytest.mark.unit
def test_invalid_email(monkeypatch):
    monkeypatch.setattr(
        dundie.utils.email, "check_valid_email", lambda _: False
    )

    with pytest.raises(InvalidEmailError):
        Person.model_validate(
            {
                "email": "whatever@email",
                "name": "John Doe",
                "dept": "Engineering",
                "role": "Developer",
                "currency": "USD",
            }
        )


@pytest.mark.unit
def test_str_method(monkeypatch):
    monkeypatch.setattr(
        "dundie.utils.email.check_valid_email", lambda email: True
    )

    person = Person(
        email="joe@doe.com",
        name="John Doe",
        dept="Engineering",
        role="Developer",
        currency="USD",
    )

    expected = "John Doe - Developer"
    assert str(person) == expected
