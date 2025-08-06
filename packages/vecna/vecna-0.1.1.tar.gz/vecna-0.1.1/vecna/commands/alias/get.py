from typing import Annotated

import typer
from rich import print as rich_print

from ...core.session import is_session_active
from ...core.vault import Vault
from ...utils import copy_to_clipboard

app = typer.Typer()


@app.command()
def get(
    name: Annotated[
        str,
        typer.Argument(
            help="The name of the alias",
            show_default=False,
        ),
    ],
    show: Annotated[
        bool,
        typer.Option(
            "--show",
            "-s",
            help="Show the alias command instead of copying to clipboard",
        ),
    ] = False,
    details: Annotated[
        bool,
        typer.Option(
            "--details",
            "-d",
            help="Show full alias details in JSON format",
        ),
    ] = False,
):
    """
    Retrieve a alias from the vault.

    By default, the alias command is copied to your clipboard without being shown.
    Use options to display the alias details or the command itself.
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

    alias = vault.get_alias(name)
    if alias is None:
        typer.secho(
            f"Alias '{name}' not found.",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(1)

    if details:
        rich_print(alias.model_dump_json(indent=2))
        return

    if show:
        typer.secho(f"Command: {alias.command}", fg=typer.colors.CYAN)
        return

    # Default behavior: copy to clipboard
    if not copy_to_clipboard(alias.command):
        typer.secho(
            "Could not copy command to clipboard. Use --show to show it.",
            fg=typer.colors.YELLOW,
        )
        return

    typer.secho("Command copied to clipboard.", fg=typer.colors.GREEN)
