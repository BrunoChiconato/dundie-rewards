from subprocess import check_output
import pytest # type: ignore


@pytest.mark.integration
@pytest.mark.medium
def test_load():
    """Test cli load command."""
    out = check_output(
        ["dundie", "load", "tests/assets/people.csv"]
    ).decode("utf-8").split("\n")
    assert len(out) == 2