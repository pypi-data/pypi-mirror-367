from typing import Annotated

import typer

from ..core.session import create_session
from ..core.vault import Vault

app = typer.Typer()


@app.command()
def init(
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite the existing vault if it already exists.",
        ),
    ] = False,
):
    """
    Initialize a new encrypted vault.
    """
    vault = Vault()

    if vault.exists() and not force:
        typer.secho(
            "Vault already exists. Use --force to overwrite.",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit()

    typer.echo("Initializing vault...")

    master = typer.prompt(
        "Enter master password",
        hide_input=True,
    )
    confirm = typer.prompt(
        "Confirm master password",
        hide_input=True,
    )

    if master != confirm:
        typer.secho(
            "Passwords do not match. Vault initialization aborted.",
            fg=typer.colors.RED,
        )
        raise typer.Exit()

    vault.create(master).unlock(master)
    create_session()

    typer.secho(
        "Vault created and unlocked successfully.",
        fg=typer.colors.GREEN,
    )
