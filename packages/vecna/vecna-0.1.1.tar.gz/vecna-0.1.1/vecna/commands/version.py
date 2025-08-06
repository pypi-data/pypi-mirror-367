import typer

from ..config import CLI_VERSION

app = typer.Typer()


@app.command()
def version():
    """
    Display the current version of Vecna.
    """
    typer.echo(f"vecna version {CLI_VERSION}")
