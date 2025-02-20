import pytest

from dundie.models import InvalidEmailError, Person


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


def test_invalid_email(monkeypatch):
    monkeypatch.setattr(
        "dundie.utils.email.check_valid_email", lambda email: False
    )

    with pytest.raises(InvalidEmailError) as excinfo:
        Person(
            email="invalid-email",
            name="John Doe",
            dept="Engineering",
            role="Developer",
            currency="USD",
        )

    assert "Invalid email:" in str(excinfo.value)


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
