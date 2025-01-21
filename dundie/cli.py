import pkg_resources
import rich_click as click
from rich.console import Console
from rich.table import Table

from dundie import core

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.SHOW_METAVARS_COLUMN = True
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
    headers = ["name", "department", "role", "e-mail"]

    for header in headers:
        table.add_column(header, style="cyan")

    result = core.load(filepath)
    for person in result:
        table.add_row(*[field.strip() for field in person.split(",")])

    console = Console()
    console.print(table)
