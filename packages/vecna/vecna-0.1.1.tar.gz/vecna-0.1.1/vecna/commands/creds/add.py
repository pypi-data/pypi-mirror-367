from typing import Annotated

import typer

from ...core.session import is_session_active
from ...core.vault import Vault
from ...models import Credential
from ...utils import generate_password

app = typer.Typer()


def prompt_for_username() -> str:
    return typer.prompt("Username (or email)").strip()


def prompt_for_password(autogenerate: bool) -> str:
    if autogenerate:
        typer.secho("A secure password has been generated.", fg=typer.colors.CYAN)
        return generate_password()

    pwd = typer.prompt(
        "Password (leave empty to generate a secure password)",
        default="",
        hide_input=True,
        show_default=False,
    ).strip()

    if not pwd:
        typer.secho("A secure password has been generated.", fg=typer.colors.CYAN)
        return generate_password()

    confirm = typer.prompt("Confirm password", hide_input=True)
    if pwd != confirm:
        typer.secho("Passwords do not match.", fg=typer.colors.RED)
        raise typer.Exit(1)

    return pwd


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
        typer.Argument(help="The name of the credential", show_default=False),
    ],
    username: Annotated[
        str,
        typer.Option(
            "--username",
            "-u",
            help="Username or email associated with the credential",
            show_default=False,
        ),
    ] = "",
    password: Annotated[
        str,
        typer.Option(
            "--password",
            "-p",
            help=(
                "Password for the credential. If not provided, a secure password will be generated."
            ),
            show_default=False,
            hide_input=True,
        ),
    ] = "",
    autogenerate_pwd: Annotated[
        bool,
        typer.Option(
            "--autogenerate-pwd",
            "-a",
            help="Generate a secure password if not provided",
            show_default=False,
        ),
    ] = False,
    notes: Annotated[
        str | None,
        typer.Option(
            "--notes",
            "-n",
            help="Notes associated with the credential",
            show_default=False,
        ),
    ] = None,
    tags: Annotated[
        str | None,
        typer.Option(
            "--tags",
            "-t",
            help="Comma-separated tags for the credential",
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
    Add a new credential to the vault.
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
        username = prompt_for_username()
        password = prompt_for_password(autogenerate_pwd)
        notes = prompt_for_notes(notes)
        tags = prompt_for_tags(tags)
    else:
        if not username:
            username = prompt_for_username()

        if autogenerate_pwd:
            password = generate_password()
            typer.secho("A secure password has been generated.", fg=typer.colors.CYAN)
        elif not password:
            password = prompt_for_password(autogenerate=False)

        notes = prompt_for_notes(notes, prompt=False)
        tags = prompt_for_tags(tags, prompt=False)

    if not name.strip():
        typer.secho("Credential name cannot be empty.", fg=typer.colors.RED)
        raise typer.Exit(1)

    credential = Credential(
        name=name,
        username=username,
        password=password,
        notes=notes,
        tags=tags,
    )
    try:
        vault.add_credential(credential)
    except KeyError as e:
        typer.secho(f"Credential with name '{name}' already exists.", fg=typer.colors.YELLOW)
        raise typer.Exit(1) from e

    typer.secho(f"Credential '{name}' added successfully.", fg=typer.colors.GREEN)
