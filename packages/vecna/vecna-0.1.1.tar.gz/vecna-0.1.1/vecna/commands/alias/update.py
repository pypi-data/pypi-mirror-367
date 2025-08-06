from typing import Annotated

import typer

from ...core.session import is_session_active
from ...core.vault import Vault
from ...models import Alias, UpdateAlias

app = typer.Typer()


def prompt_for_updates(
    current: Alias,
) -> UpdateAlias:
    """
    Prompt the user for updates to an existing alias.

    This function interactively asks the user for new values for each field of the alias.
    For each field, the current value is used as the default if the user provides no input.

    Args:
        current: The existing alias object to be updated

    Returns:
        UpdateAlias: An object containing the updated alias information
    """
    new_alias = UpdateAlias(name=current.name)

    new_name = typer.prompt(
        "New Alias name",
        default=current.name,
        show_default=False,
    ).strip()
    if new_name != current.name:
        new_alias.new_name = new_name

    new_alias.command = typer.prompt(
        "Update command",
        default=current.command,
    ).strip()

    new_alias.notes = typer.prompt(
        "Notes",
        default=current.notes or "",
        show_default=False,
    ).strip()

    tags_input = typer.prompt(
        "Tags (comma-separated)",
        default=",".join(current.tags or []),
        show_default=False,
    ).strip()
    new_alias.tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

    return new_alias


@app.command()
def update(
    name: Annotated[
        str,
        typer.Argument(
            help="Name of the Alias",
            show_default=False,
        ),
    ],
    new_name: Annotated[
        str | None,
        typer.Option(
            "--new-name",
            help="New Alias name",
            show_default=False,
        ),
    ] = None,
    command: Annotated[
        str | None,
        typer.Option(
            "--command",
            "-c",
            help="Updated command",
            show_default=False,
        ),
    ] = None,
    notes: Annotated[
        str | None,
        typer.Option(
            "--notes",
            "-n",
            help="Updated notes",
            show_default=False,
        ),
    ] = None,
    tags: Annotated[
        str | None,
        typer.Option(
            "--tags",
            "-t",
            help="Comma-separated updated tags",
            show_default=False,
        ),
    ] = None,
    interactive: Annotated[
        bool,
        typer.Option(
            "--interactive",
            "-i",
            help="Prompt interactively instead of using flags",
        ),
    ] = False,
):
    """
    Update an existing alias in your vault.

    You can use either --interactive mode or individual options to update fields.
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

    current_alias = vault.get_alias(name)
    if current_alias is None:
        typer.secho(
            f"Alias '{name}' not found.",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(1)

    if interactive:
        new_alias = prompt_for_updates(current_alias)
    else:
        if not any(
            [
                new_name,
                command,
                notes,
                tags,
            ]
        ):
            typer.secho(
                "Nothing to update. Use flags or --interactive.",
                fg=typer.colors.YELLOW,
            )
            raise typer.Exit(0)

        new_alias = UpdateAlias(name=name)
        new_alias.new_name = new_name
        new_alias.command = command
        new_alias.notes = notes
        if tags:
            new_alias.tags = [tag.strip() for tag in tags.split(",") if tag.strip()]

    try:
        vault.update_alias(new_alias)
    except KeyError:
        typer.secho(
            f"Failed to update alias '{name}'.",
            fg=typer.colors.RED,
        )

    typer.secho(
        f"Alias '{name}' updated successfully.",
        fg=typer.colors.GREEN,
    )
