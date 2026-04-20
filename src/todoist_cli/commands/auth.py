from __future__ import annotations

from typing import Any

import typer

from todoist_cli.auth import resolved_token_status, store_token
from todoist_cli.config import default_config_path, delete_config

app = typer.Typer(help="Manage Todoist API authentication.")


@app.command()
def login(ctx: typer.Context) -> None:
    """Store a Todoist API token for future commands."""
    token = typer.prompt("Todoist API token", hide_input=True)
    settings = _settings(ctx)
    path = store_token(
        token,
        config_path=settings.get("config_path"),
        base_url=settings.get("base_url"),
        default_format=settings.get("output_format"),
    )
    typer.echo(f"Stored Todoist API token in {path}.")


@app.command()
def status(ctx: typer.Context) -> None:
    """Show whether a Todoist API token is available."""
    settings = _settings(ctx)
    source = resolved_token_status(
        settings.get("token"),
        config_path=settings.get("config_path"),
    )
    if source is None:
        typer.echo("No Todoist API token configured.")
        raise typer.Exit(code=1)
    typer.echo(f"Todoist API token available from {source}.")


@app.command()
def logout(ctx: typer.Context) -> None:
    """Remove the stored Todoist API token."""
    settings = _settings(ctx)
    removed = delete_config(settings.get("config_path"))
    path = settings.get("config_path") or default_config_path()
    if removed:
        typer.echo(f"Removed stored Todoist API token from {path}.")
    else:
        typer.echo("No stored Todoist API token found.")


def _settings(ctx: typer.Context) -> dict[str, Any]:
    obj = ctx.obj
    if isinstance(obj, dict):
        return obj
    return {}
