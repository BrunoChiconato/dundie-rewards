"""Dundie Mifflin Rewards System CLI

This application allows managers and employees to interact with the rewards system.
Managers can:
  - Load employee data from a CSV file into the database.
  - View all employee balances.
  - Add or remove points for employees.
  - Transfer points between employees.
  - Review transaction movements.

Employees can:
  - Check their own account balance and transaction history.
  - Transfer points to other employees.
"""

import json

import pkg_resources
import rich_click as click
from rich.console import Console
from rich.table import Table

from dundie import core
from typing import Any, Dict

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.SHOW_METAVARS_COLUMN = False
click.rich_click.APPEND_METAVARS_HELP = True

Query = Dict[str, Any]


@click.group()
@click.version_option(pkg_resources.get_distribution("dundie").version)
def main() -> None:
    """Dundie Mifflin Rewards System CLI

    This application allows managers and employees to interact with the rewards system.
    - Managers can:
        - Load employee data from a CSV file into the database.
        - View all employee balances.
        - Add or remove points for employees.
        - Transfer points between employees.
        - Review transaction movements.

    - Employees can:
        - Check their own account balance and transaction history.
        - Transfer points to other employees.
    """


@main.command()
@click.argument("filepath", type=click.Path(exists=True))
def load(filepath: str) -> None:
    """Load employee data from a CSV file into the SQLite database.

    This command performs the following steps:
      - Validates the CSV file format.
      - Parses the CSV file.
      - Imports the data into the database.

    The CSV file must contain the following columns:
      - name: Employee's full name.
      - dept: Department name.
      - role: Employee role.
      - email: Employee email address.
      - currency: Currency code.

    Args:
        filepath (str): The file path to the CSV file.

    Returns:
        None
    """
    table = Table(title="Dundler Mifflin Employees")
    headers = ["email", "name", "dept", "role", "currency", "created"]

    for header in headers:
        table.add_column(header, style="cyan")

    result = core.load(filepath)
    for person in result:
        table.add_row(*[str(value) for value in person.values()])

    console = Console()
    console.print(table)


@main.command()
@click.option("--dept", required=False)
@click.option("--email", required=False)
@click.option("--output", default=None)
def show(output, **query: Query) -> None:
    """Display employees and their account balances.

    Managers can filter the results by department and email. Employees, however,
    can only view their own balance.

    Args:
        output (str): (Optional) Path to the output file. If provided, the results
            are saved to this file.
        dept (str): (Optional) Department name to filter by.
        email (str): (Optional) Employee email address to filter by.

    Returns:
        None
    """
    result = core.read(**query)

    if output:
        with open(output, "w") as output_file:
            output_file.write(json.dumps(result, indent=4))
        return

    if not result:
        print("No results found.")

    table = Table(title="Dundler Mifflin Report")
    for key in result[0]:
        table.add_column(key.title(), style="cyan")

    for person in result:
        person["value"] = f"{person['value']:.2f}"
        person["balance"] = f"{person['balance']:.2f}"
        table.add_row(*[str(value) for value in person.values()])

    console = Console()
    console.print(table)


@main.command()
@click.argument("value", type=click.INT, required=True)
@click.option("--dept", required=False)
@click.option("--email", required=False)
@click.pass_context
def add(ctx, value: int, **query: Query) -> None:
    """Add points to one or more employees or departments.

    Args:
        value (int): The number of points to add.
        dept (str): (Optional) Department name to which points should be added.
        email (str): (Optional) Email address of the employee to receive the points.

    Returns:
        None
    """
    core.add(value, **query)
    ctx.invoke(show, **query)


@main.command()
@click.argument("value", type=click.INT, required=True)
@click.option("--dept", required=False)
@click.option("--email", required=False)
@click.pass_context
def remove(ctx, value: int, **query: Query) -> None:
    """Remove points from one or more employees or departments.

    Args:
        value (int): The number of points to remove.
        dept (str): (Optional) Department name from which points should be removed.
        email (str): (Optional) Email address of the employee from whom points should be removed.

    Returns:
        None
    """
    core.add(-value, **query)
    ctx.invoke(show, **query)


@main.command()
@click.option("--value", type=click.INT, required=True)
@click.option("--to", required=True)
def transfer(value: int, to: str) -> None:
    """Transfer points between employees.

    Args:
        value (int): The number of points to transfer.
        to (str): The email address of the employee who will receive the points.

    Returns:
        None
    """
    core.transfer(value, to)


@main.command()
@click.pass_context
def movements(ctx) -> None:
    """Display the transaction movements history.

    Managers can view the complete transaction history for all employees, whereas
    employees can only view their own transactions.

    Returns:
        None
    """
    result = core.movements()

    if not result:
        print("No results found.")

    table = Table(title="Dundler Mifflin Movements")
    for key in result[0]:
        table.add_column(key.title(), style="cyan")

    for person in result:
        person["Converted Movement"] = f"{person['Converted Movement']:.2f}"
        table.add_row(*[str(value) for value in person.values()])

    console = Console()
    console.print(table)

    ctx.invoke(show)
