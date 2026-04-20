from __future__ import annotations

from typing import Any

import click
import typer

from todoist_cli.auth import resolve_token
from todoist_cli.client import TodoistClient
from todoist_cli.errors import TodoistCLIError


def settings(ctx: typer.Context) -> dict[str, Any]:
    obj = ctx.obj
    if isinstance(obj, dict):
        return obj
    return {}


def client_from_context(ctx: typer.Context) -> TodoistClient:
    command_settings = settings(ctx)
    try:
        token = resolve_token(
            command_settings.get("token"),
            config_path=command_settings.get("config_path"),
        )
    except TodoistCLIError as exc:
        raise click.ClickException(str(exc)) from exc

    base_url = command_settings.get("base_url")
    if not isinstance(base_url, str):
        base_url = "https://api.todoist.com/api/v1"

    return TodoistClient(
        token=token.token,
        base_url=base_url,
    )


def output_options(ctx: typer.Context) -> dict[str, Any]:
    command_settings = settings(ctx)
    return {
        "output_format": command_settings.get("output_format", "table"),
        "no_color": command_settings.get("no_color", False),
    }


def raise_click_error(exc: TodoistCLIError) -> None:
    raise click.ClickException(str(exc)) from exc


def compact_dict(values: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}
