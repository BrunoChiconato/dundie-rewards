import pytest

MARKER = """\
integration: Mark integration tests
high: Mark high priority tests
medium: Mark medium priority tests
low: Mark low priority tests
"""


def pytest_configure(config):
    for line in MARKER.split("\n"):
        config.addinivalue_line("markers", line)

@pytest.fixture(autouse=True)
def go_to_tmpdir(request): # injecao de dependencias
    tmpdir = request.getfixturevalue("tmpdir")
    with tmpdir.as_cwd():
        yield # protocolo de generator