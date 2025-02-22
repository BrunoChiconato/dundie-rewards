import pytest

from dundie.utils.email import check_valid_email
from dundie.utils.user import (
    generate_simple_password,
    get_password_hash,
    verify_password,
)


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
