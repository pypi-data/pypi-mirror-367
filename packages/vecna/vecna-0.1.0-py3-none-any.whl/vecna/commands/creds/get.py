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
            help="The name of the credential",
            show_default=False,
        ),
    ],
    password: Annotated[
        bool,
        typer.Option(
            "--password",
            "-p",
            help="Show the password in plain text",
        ),
    ] = False,
    details: Annotated[
        bool,
        typer.Option(
            "--details",
            "-d",
            help="Show full credential details in JSON format",
        ),
    ] = False,
):
    """
    Retrieve a credential from the vault.

    By default, the password is copied to your clipboard without being shown.
    Use options to display the username, password, or detailed information.
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

    credential = vault.get_credential(name)
    if credential is None:
        typer.secho(
            f"Credential '{name}' not found.",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(1)

    if details:
        rich_print(credential.model_dump_json(indent=2))
        return

    typer.secho(f"Username: {credential.username}", fg=typer.colors.CYAN)

    if password:
        typer.secho(f"Password: {credential.password}", fg=typer.colors.CYAN)
        return

    # Default behavior: copy to clipboard
    if not copy_to_clipboard(credential.password):
        typer.secho(
            "Could not copy password to clipboard. Use --password to display it.",
            fg=typer.colors.YELLOW,
        )
        return

    typer.secho("Password copied to clipboard.", fg=typer.colors.GREEN)
