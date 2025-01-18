MARKER = """\
integration: Mark integration tests
high: Mark high priority tests
medium: Mark medium priority tests
low: Mark low priority tests
"""


def pytest_configure(config):
    for line in MARKER.split("\n"):
        config.addinivalue_line("markers", line)