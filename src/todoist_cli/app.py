from enum import StrEnum
from typing import Annotated

import typer

from todoist_cli import __version__
from todoist_cli.commands import auth

DEFAULT_BASE_URL = "https://api.todoist.com/api/v1"


class OutputFormat(StrEnum):
    table = "table"
    json = "json"
    ndjson = "ndjson"


app = typer.Typer(
    name="todoist",
    help="Command-line interface for Todoist API operations.",
    no_args_is_help=True,
    invoke_without_command=True,
)
app.add_typer(auth.app, name="auth")


@app.callback()
def main(
    ctx: typer.Context,
    token: Annotated[
        str | None,
        typer.Option(
            "--token",
            help="Todoist API token. Overrides environment and stored config.",
        ),
    ] = None,
    output_format: Annotated[
        OutputFormat,
        typer.Option(
            "--format",
            help="Output format.",
            case_sensitive=False,
        ),
    ] = OutputFormat.table,
    base_url: Annotated[
        str,
        typer.Option(
            "--base-url",
            help="Todoist API base URL.",
        ),
    ] = DEFAULT_BASE_URL,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            help="Include additional debugging details.",
        ),
    ] = False,
    no_color: Annotated[
        bool,
        typer.Option(
            "--no-color",
            help="Disable colored output.",
        ),
    ] = False,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the installed version and exit.",
        ),
    ] = False,
) -> None:
    """Run Todoist CLI commands."""
    ctx.obj = {
        "token": token,
        "output_format": output_format.value,
        "base_url": base_url,
        "verbose": verbose,
        "no_color": no_color,
    }

    if version:
        typer.echo(__version__)
        raise typer.Exit()
