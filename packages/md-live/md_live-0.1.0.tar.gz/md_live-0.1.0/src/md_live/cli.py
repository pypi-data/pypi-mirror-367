"""Console script for md_live."""

import typer
from rich.console import Console

from md_live import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for md_live."""
    console.print("Replace this message by putting your code into "
               "md_live.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
