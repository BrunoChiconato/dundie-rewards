import pytest
import httpx

from dundie.models import Person
from dundie.utils.exchange import get_rates, USDRate
from dundie.utils.email import check_valid_email
from dundie.utils.user import (
    generate_simple_password,
    get_password_hash,
    verify_password,
)


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
