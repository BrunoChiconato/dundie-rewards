import json

import pkg_resources  # type: ignore
import rich_click as click  # type: ignore
from rich.console import Console  # type: ignore
from rich.table import Table  # type: ignore

from dundie import core

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.SHOW_METAVARS_COLUMN = False
click.rich_click.APPEND_METAVARS_HELP = True


@click.group()
@click.version_option(pkg_resources.get_distribution("dundie").version)
def main():
    """Dundie Mifflin Rewards System

    This CLI application controls Dundie Mifflin Rewards System.
    """


@main.command()
@click.argument("filepath", type=click.Path(exists=True))
def load(filepath):
    """Load employees from a CSV file.

    - Validates the CSV file.
    - Parses the CSV file.
    - Loads to the database.
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
    """Show all employees."""
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
        person["value"] = f"{person["value"]:.2f}"
        person["balance"] = f"{person["balance"]:.2f}"
        table.add_row(*[str(value) for value in person.values()])

    console = Console()
    console.print(table)


@main.command()
@click.argument("value", type=click.INT, required=True)
@click.option("--dept", required=False)
@click.option("--email", required=False)
@click.pass_context
def add(ctx, value, **query):
    """Add points to employees or departments."""
    core.add(value, **query)
    ctx.invoke(show, **query)


@main.command()
@click.argument("value", type=click.INT, required=True)
@click.option("--dept", required=False)
@click.option("--email", required=False)
@click.pass_context
def remove(ctx, value, **query):
    """Remove points to employees or departments."""
    core.add(-value, **query)
    ctx.invoke(show, **query)
