import typer

from ..core.session import create_session
from ..core.vault import Vault

app = typer.Typer()


@app.command()
def unlock():
    """
    Unlock the encrypted vault and begin a session.
    """
    master = typer.prompt(
        "Master password",
        hide_input=True,
    )
    try:
        Vault().load(raise_no_key=False).unlock(master)
        typer.secho(
            "Vault unlocked successfully.",
            fg=typer.colors.GREEN,
        )
    except ValueError as e:
        typer.secho(
            "Invalid password. Access denied.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1) from e
    create_session()
