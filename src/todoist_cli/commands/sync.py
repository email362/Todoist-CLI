from __future__ import annotations

import json
from typing import Annotated

import typer

from todoist_cli.commands._utils import (
    client_from_context,
    output_options,
    raise_click_error,
)
from todoist_cli.errors import TodoistCLIError
from todoist_cli.output import render_output

app = typer.Typer(help="Run thin Todoist sync requests.")


@app.command("all")
def sync_all(
    ctx: typer.Context,
    sync_token: Annotated[
        str,
        typer.Option(
            "--sync-token",
            help="Todoist sync token. Use '*' for a full sync.",
        ),
    ] = "*",
) -> None:
    """Sync all resource types."""
    _sync(ctx, sync_token=sync_token, resource_types=["all"])


@app.command("resources")
def sync_resources(
    ctx: typer.Context,
    types: Annotated[
        str,
        typer.Option(
            "--types",
            help="Comma-separated resource types, such as all or projects,items.",
        ),
    ] = "all",
    sync_token: Annotated[
        str,
        typer.Option(
            "--sync-token",
            help="Todoist sync token. Use '*' for a full sync.",
        ),
    ] = "*",
) -> None:
    """Sync selected resource types."""
    resource_types = [item.strip() for item in types.split(",") if item.strip()]
    if not resource_types:
        raise typer.BadParameter(
            "Provide at least one resource type.",
            param_hint="--types",
        )
    _sync(ctx, sync_token=sync_token, resource_types=resource_types)


def _sync(
    ctx: typer.Context,
    *,
    sync_token: str,
    resource_types: list[str],
) -> None:
    try:
        data = client_from_context(ctx).post(
            "/sync",
            data={
                "sync_token": sync_token,
                "resource_types": json.dumps(resource_types),
            },
        )
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, **output_options(ctx))
