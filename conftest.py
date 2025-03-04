import warnings
import pytest
from unittest.mock import patch
from sqlmodel import create_engine
from dundie import models
from sqlalchemy.exc import SAWarning


warnings.filterwarnings("ignore", category=SAWarning)


MARKER = """\
unit: Mark unit tests
high: Mark high priority tests
medium: Mark medium priority tests
low: Mark low priority tests
"""


def pytest_configure(config):
    for line in MARKER.split("\n"):
        config.addinivalue_line("markers", line)


@pytest.fixture(autouse=True)
def go_to_tmpdir(request):  # injecao de dependencias
    tmpdir = request.getfixturevalue("tmpdir")
    with tmpdir.as_cwd():
        yield  # protocolo de generators


@pytest.fixture(autouse=True, scope="function")
def setup_testing_database(request):
    """For each test, create a database file on tmpdir.
    Force database.py to use that filepath.
    """
    tmpdir = request.getfixturevalue("tmpdir")
    test_db = str(tmpdir.join("database.test.db"))

    engine = create_engine(f"sqlite:///{test_db}")
    models.SQLModel.metadata.create_all(engine)
    with patch("dundie.database.engine", engine):
        yield
