import typer
from rich import print as rich_print

from ...core.session import is_session_active
from ...core.vault import Vault

app = typer.Typer()


@app.command()
def list():
    """
    List all aliass stored in the vault in readable format.
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

    aliases = vault.list_aliases()
    if not aliases:
        typer.secho(
            "No aliases found in the vault.",
            fg=typer.colors.YELLOW,
        )
        return

    rich_print("-" * 40)
    for alias in aliases:
        rich_print(f"[bold cyan]Name:[/bold cyan] {alias.name}")
        rich_print(f"[bold cyan]Command:[/bold cyan] {alias.command}")
        if alias.notes:
            rich_print(f"[bold cyan]Notes:[/bold cyan] {alias.notes}")
        if alias.tags:
            rich_print("[bold cyan]Tags:[/bold cyan] {}".format(", ".join(alias.tags)))
        rich_print("-" * 40)
