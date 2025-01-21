import os

import pytest
from click.testing import CliRunner

from dundie.cli import load, main

cmd = CliRunner()


@pytest.mark.integration
@pytest.mark.medium
def test_load_positive_call_load_command():
    """Test cli load command."""
    csv_path = os.path.join(
        os.path.dirname(__file__), "..", "tests", "assets", "people.csv"
    )
    out = cmd.invoke(load, csv_path)
    assert "Dundler Mifflin Employees" in out.output


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
    out = cmd.invoke(main, wrong_command, csv_path)

    assert out.exit_code != 0
    assert f"No such command '{wrong_command}'." in out.output
