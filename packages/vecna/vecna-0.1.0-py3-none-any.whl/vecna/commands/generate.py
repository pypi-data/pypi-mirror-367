from typing import Annotated

import typer

from ..utils import copy_to_clipboard, generate_password

app = typer.Typer()


@app.command()
def generate(
    length: Annotated[
        int,
        typer.Option(
            "--length",
            "-l",
            help="Length of the generated password",
            show_default=True,
        ),
    ] = 15,
    include_symbols: Annotated[
        bool,
        typer.Option(
            "--symbols",
            "-s",
            help="Include symbols in the generated password",
            show_default=True,
        ),
    ] = False,
    include_numbers: Annotated[
        bool,
        typer.Option(
            "--numbers",
            "-n",
            help="Include numbers in the generated password",
            show_default=True,
        ),
    ] = False,
    show_password: Annotated[
        bool,
        typer.Option(
            "--show",
            "-S",
            help="Show the generated password in plain text",
        ),
    ] = False,
):
    """
    Generate a secure password.
    By default, it generates a 15-character password with symbols and numbers.
    """
    password = generate_password(
        length=length, use_special_chars=include_symbols, use_numbers=include_numbers
    )

    if show_password:
        typer.secho("Generated Password:", fg=typer.colors.CYAN)
        typer.echo(password)

    copy_to_clipboard(password)
    typer.secho("Password copied to clipboard.", fg=typer.colors.GREEN)
