import pytest
import httpx

from unittest.mock import MagicMock
from dundie.models import Person
from dundie.utils.exchange import get_rates, USDRate
from dundie.utils.email import check_valid_email
from dundie.utils.user import (
    generate_simple_password,
    get_password_hash,
    verify_password,
)
from dundie.utils.auth import requires_auth, AuthenticationError


class FakeResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data

    def json(self):
        return self._json


@pytest.mark.unit
def test_password_hash():
    password = "batatinha123"
    hashed = get_password_hash(password)
    assert password != hashed
    assert verify_password(password, hashed)


@pytest.mark.unit
@pytest.mark.parametrize(
    "address", ["brunochiconato01@gmail.com", "joe@doe.com", "a@b.pt"]
)
def test_positive_check_valid_email(address):
    """Ensure email is valid."""
    assert check_valid_email(address) is True


@pytest.mark.unit
@pytest.mark.parametrize("address", ["brunochiconato@com", "@doe.com", "a@b"])
def test_negative_check_valid_email(address):
    """Ensure email is invalid."""
    assert check_valid_email(address) is False


@pytest.mark.unit
def test_generate_simple_password():
    """Test generation of random simple passwords
    TODO: Generate hashed complex passwords, encrypt them and test them.
    """
    passwords = []
    for _ in range(100):
        passwords.append(generate_simple_password(8))

    assert len(set(passwords)) == 100


@pytest.mark.unit
def test_valid_email(monkeypatch):
    monkeypatch.setattr("dundie.models.check_valid_email", lambda email: True)

    person = Person.model_validate(
        {
            "email": "teste@example.com",
            "name": "Teste",
            "dept": "TI",
            "role": "Developer",
        }
    )

    assert person.email == "teste@example.com"


def fake_get_success(url, **kwargs):
    if "BRL" in url:
        currency = "BRL"
    elif "EUR" in url:
        currency = "EUR"
    elif "JPY" in url:
        currency = "JPY"
    elif "INR" in url:
        currency = "INR"
    else:
        currency = "XXX"  # fallback

    data = {
        f"USD{currency}": {
            "code": "USD",
            "codein": currency,
            "name": f"Dólar Americano/{currency}",
            "high": "5.0",
        }
    }
    return FakeResponse(200, data)


def fake_get_failure(url, **kwargs):
    return FakeResponse(404, {})


@pytest.mark.unit
def test_get_rates_success(monkeypatch):
    monkeypatch.setattr(httpx, "get", fake_get_success)
    currencies = ["BRL", "EUR", "JPY", "INR"]
    rates = get_rates(currencies)
    for currency in currencies:
        assert isinstance(rates[currency], USDRate)
        assert rates[currency].name == f"Dólar Americano/{currency}"
        assert float(rates[currency].values) == 5.0


@pytest.mark.unit
def test_get_rates_failure(monkeypatch):
    monkeypatch.setattr(httpx, "get", fake_get_failure)
    currencies = ["BRL"]
    rates = get_rates(currencies)

    assert rates["BRL"].name == "Error"
    assert float(rates["BRL"].values) == 0


@pytest.mark.unit
def test_env_vars_not_found(monkeypatch):
    monkeypatch.delenv("DUNDIE_EMAIL", raising=False)
    monkeypatch.delenv("DUNDIE_PASSWORD", raising=False)

    fake_session = MagicMock()

    fake_session.exec.return_value.first.return_value = object()

    class FakeSessionCM:
        def __enter__(self):
            return fake_session

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        "dundie.utils.auth.get_session", lambda: FakeSessionCM()
    )

    decorated_func = requires_auth(
        lambda *args, **kwargs: kwargs.get("from_person")
    )

    with pytest.raises(AuthenticationError) as exc_info:
        decorated_func()
    assert "Variables DUNDIE_EMAIL and DUNDIE_PASSWORD not definied." in str(
        exc_info.value
    )


@pytest.mark.unit
def test_auth_user_not_found(monkeypatch):
    monkeypatch.setenv("DUNDIE_EMAIL", "test@test.com")
    monkeypatch.setenv("DUNDIE_PASSWORD", "1234")

    fake_session_first = MagicMock()
    fake_session_first.exec.return_value.first.return_value = object()

    fake_session_second = MagicMock()
    fake_session_second.exec.return_value.first.return_value = None

    class FakeSessionCM:
        def __init__(self, session):
            self.session = session

        def __enter__(self):
            return self.session

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    call_count = 0

    def fake_get_session():
        nonlocal call_count
        if call_count == 0:
            call_count += 1
            return FakeSessionCM(fake_session_first)
        else:
            return FakeSessionCM(fake_session_second)

    monkeypatch.setattr("dundie.utils.auth.get_session", fake_get_session)

    decorated_func = requires_auth(
        lambda *args, **kwargs: kwargs.get("from_person")
    )

    with pytest.raises(AuthenticationError) as exc_info:
        decorated_func()

    assert "User doesn't exist." in str(exc_info.value)


@pytest.mark.unit
def test_auth_incorrect_password(monkeypatch):
    class DummyUser:
        password = "hashed_password"

    class DummyPerson:
        user = DummyUser()

    class FakeSessionCM:
        def __init__(self, session):
            self.session = session

        def __enter__(self):
            return self.session

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    call_count = 0

    def fake_get_session():
        nonlocal call_count
        if call_count == 0:
            call_count += 1
            return FakeSessionCM(fake_session_first)
        else:
            return FakeSessionCM(fake_session_second)

    monkeypatch.setenv("DUNDIE_EMAIL", "test@test.com")
    monkeypatch.setenv("DUNDIE_PASSWORD", "1234")

    fake_session_first = MagicMock()
    fake_session_first.exec.return_value.first.return_value = object()

    fake_session_second = MagicMock()
    fake_session_second.exec.return_value.first.return_value = DummyPerson()

    monkeypatch.setattr("dundie.utils.auth.get_session", fake_get_session)

    monkeypatch.setattr(
        "dundie.utils.auth.verify_password", lambda pwd, db_pwd: False
    )

    decorated_func = requires_auth(
        lambda *args, **kwargs: kwargs.get("from_person")
    )

    with pytest.raises(AuthenticationError) as exc_info:
        decorated_func()

    assert "Authentication Error." in str(exc_info.value)
