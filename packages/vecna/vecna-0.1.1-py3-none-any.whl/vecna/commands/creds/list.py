import typer
from rich import print as rich_print

from ...core.session import is_session_active
from ...core.vault import Vault

app = typer.Typer()


@app.command()
def list():
    """
    List all credentials stored in the vault in readable format.
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

    credentials = vault.list_credentials()
    if not credentials:
        typer.secho(
            "No credentials found in the vault.",
            fg=typer.colors.YELLOW,
        )
        return

    rich_print("-" * 40)
    for credential in credentials:
        rich_print(f"[bold cyan]Name:[/bold cyan] {credential.name}")
        rich_print(f"[bold cyan]Username:[/bold cyan] {credential.username}")
        if credential.notes:
            rich_print(f"[bold cyan]Notes:[/bold cyan] {credential.notes}")
        if credential.tags:
            rich_print("[bold cyan]Tags:[/bold cyan] {}".format(", ".join(credential.tags)))
        rich_print("-" * 40)
