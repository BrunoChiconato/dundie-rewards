"""CLI application for Dundie Mifflin Rewards System."""

import json

import pkg_resources
import rich_click as click
from rich.console import Console
from rich.table import Table

from dundie import core

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.SHOW_METAVARS_COLUMN = False
click.rich_click.APPEND_METAVARS_HELP = True


@click.group()
@click.version_option(pkg_resources.get_distribution("dundie").version)
def main() -> None:
    """Dundie Mifflin Rewards System

    This CLI application controls Dundie Mifflin Rewards System.

    - Managers can load information to the database,
    see all employees balances, add and remove points from employees, transfer
    points between employees, and see their movements.
    - Employees can see their own balance and movements
    and transfer points to other employees.
    """


@main.command()
@click.argument("filepath", type=click.Path(exists=True))
def load(filepath):
    """Load employees from a CSV file to a SQLite database.

    - Validates the CSV file.
    - Parses the CSV file.
    - Loads to the database.

    The CSV file must have the following columns:
    - name: Employee name.
    - dept: Department name.
    - role: Employee role.
    - email: Employee email.
    - currency: Currency code.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        None: If the CSV file is not valid.

    Raises:
        ValueError: If the CSV file is not valid.
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
def show(output, **query):
    """Show employees and their balances.

    - Managers can filter by department and email.
    - Employees can only see their own balance.

    Args:
        output (str): Output file path.
        dept (str): Department name.
        email (str): Employee email.

    Returns:
        None: If no results are found.

    Raises:
        ValueError: If the output file path is not valid.
    """
    result, _ = core.read(**query)

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
def add(ctx, value, **query):
    """Add points to employees or departments.

    Args:
        value (int): Points to add.
        dept (str): Department name.
        email (str): Employee email.

    Returns:
        None: If no results are found.
    """
    core.add(value, **query)
    ctx.invoke(show, **query)


@main.command()
@click.argument("value", type=click.INT, required=True)
@click.option("--dept", required=False)
@click.option("--email", required=False)
@click.pass_context
def remove(ctx, value, **query):
    """Remove points to employees or departments.

    Args:
        value (int): Points to remove.
        dept (str): Department name.
        email (str): Employee email.

    Returns:
        None: If no results are found.
    """
    core.add(-value, **query)
    ctx.invoke(show, **query)


@main.command()
@click.option("--value", type=click.INT, required=True)
@click.option("--to", required=True)
def transfer(value: int, to: str):
    """Transfer points between employees.

    Args:
        value (int): Points to transfer.
        to (str): Employee email.

    Returns:
        None: If no results are found.
    """
    core.transfer(value, to)


@main.command()
def movements():
    """Show all movements from employees.

    Returns:
        None: If no results are found"""
    result = core.movements()

    if not result:
        print("No results found.")

    table = Table(title="Dundler Mifflin Movements")
    for key in result[0]:
        table.add_column(key.title(), style="cyan")

    for person in result:
        person["value"] = f"{person['value']:.2f}"
        table.add_row(*[str(value) for value in person.values()])

    console = Console()
    console.print(table)
