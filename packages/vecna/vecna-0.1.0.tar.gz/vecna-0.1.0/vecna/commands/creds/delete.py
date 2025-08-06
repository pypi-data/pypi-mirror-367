import typer

from ...core.session import is_session_active
from ...core.vault import Vault

app = typer.Typer()


@app.command()
def delete(name: str):
    """
    Delete a credential from the vault.
    """
    if not is_session_active():
        typer.secho(
            "No active session. Please unlock the vault first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    try:
        vault = Vault().load()
    except Exception as e:
        typer.secho(
            "Vault is locked or inaccessible. Please unlock it first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1) from e

    try:
        vault.delete_credential(name)
    except KeyError as e:
        typer.secho(
            f"Credential '{name}' not found.",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(1) from e
    typer.secho(
        f"Credential '{name}' deleted successfully.",
        fg=typer.colors.GREEN,
    )
