import os
from subprocess import CalledProcessError, check_output

import pytest  # type: ignore


@pytest.mark.integration
@pytest.mark.medium
def test_load_positive_call_load_command():
    """Test cli load command."""
    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "tests", "assets", "people.csv"
    )
    out = (
        check_output(["dundie", "load", csv_path]).decode("utf-8").split("\n")
    )
    assert len(out) == 2


@pytest.mark.integration
@pytest.mark.medium
@pytest.mark.parametrize(
    "wrong_command", ["loady", "carrega", "lad", "l0ad", "lod"]
)
def test_load_negative_call_load_command_with_wrong_params(wrong_command):
    """Test cli load command."""
    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "tests", "assets", "people.csv"
    )
    with pytest.raises(CalledProcessError) as error:
        check_output(["dundie", wrong_command, csv_path]).decode(
            "utf-8"
        ).split("\n")

    assert "status 2" in str(error.getrepr())
