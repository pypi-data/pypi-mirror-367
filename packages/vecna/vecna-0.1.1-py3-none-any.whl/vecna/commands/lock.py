import typer

from ..core.session import end_session
from ..core.vault import Vault

app = typer.Typer()


@app.command()
def lock():
    """
    Lock the vault and end the active session.
    """
    Vault().lock()
    end_session()
    typer.secho(
        "Vault locked and session ended.",
        fg=typer.colors.GREEN,
    )
