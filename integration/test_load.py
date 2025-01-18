from subprocess import check_output
import pytest # type: ignore
import os


@pytest.mark.integration
@pytest.mark.medium
def test_load():
    """Test cli load command."""
    csv_path = os.path.join(os.path.dirname(__file__), "..", "tests", "assets", "people.csv")
    out = check_output(
        ["dundie", "load", csv_path]
    ).decode("utf-8").split("\n")
    assert len(out) == 2