from typing import Annotated

import typer

from ...core.session import is_session_active
from ...core.vault import Vault
from ...models import Alias

app = typer.Typer()


def prompt_for_command(existing: str) -> str:
    return existing.strip() if existing else typer.prompt("Command").strip()


def prompt_for_notes(existing: str | None, prompt: bool = True) -> str:
    if existing is not None:
        return existing.strip()
    if prompt:
        return typer.prompt("Notes (optional)", default="", show_default=False).strip()
    return ""


def prompt_for_tags(existing: str | None, prompt: bool = True) -> list[str]:
    if existing:
        return [tag.strip() for tag in existing.split(",") if tag.strip()]
    if prompt:
        tags_input = typer.prompt(
            "Tags (comma-separated, optional)", default="", show_default=False
        ).strip()
        return [tag.strip() for tag in tags_input.split(",") if tag.strip()]
    return []


@app.command()
def add(
    name: Annotated[
        str,
        typer.Argument(
            help="The name of the alias",
            show_default=False,
        ),
    ],
    command: Annotated[
        str,
        typer.Option(
            "--command",
            "-c",
            help="The command associated with the alias",
            show_default=False,
        ),
    ] = "",
    notes: Annotated[
        str | None,
        typer.Option(
            "--notes",
            "-n",
            help="Notes associated with the alias",
            show_default=False,
        ),
    ] = None,
    tags: Annotated[
        str | None,
        typer.Option(
            "--tags",
            "-t",
            help="Tags associated with the alias, comma-separated",
            show_default=False,
        ),
    ] = None,
    interactive: Annotated[
        bool,
        typer.Option(
            "--interactive",
            "-i",
            help="Run in interactive mode (prompts for all fields)",
            show_default=False,
        ),
    ] = False,
):
    """
    Add a new alias to the vault.
    """
    if not is_session_active():
        typer.secho("No active session. Please unlock the vault first.", fg=typer.colors.RED)
        raise typer.Exit(1)

    try:
        vault = Vault().load()
    except Exception as e:
        typer.secho("Vault is locked or inaccessible. Please unlock it first.", fg=typer.colors.RED)
        raise typer.Exit(1) from e

    if interactive:
        command = prompt_for_command(command)
        notes = prompt_for_notes(notes)
        tags = prompt_for_tags(tags)
    else:
        if not command:
            command = prompt_for_command(command)
        notes = prompt_for_notes(notes, prompt=False)
        tags = prompt_for_tags(tags, prompt=False)

    if not name.strip():
        typer.secho("Alias name cannot be empty.", fg=typer.colors.RED)
        raise typer.Exit(1) from None

    alias = Alias(
        name=name.strip(),
        command=command,
        notes=notes,
        tags=tags,
    )

    try:
        vault.add_alias(alias)
    except KeyError as e:
        typer.secho(f"Alias with name '{name}' already exists.", fg=typer.colors.YELLOW)
        raise typer.Exit(1) from e

    typer.secho(f"Alias '{name}' added successfully.", fg=typer.colors.GREEN)
