from __future__ import annotations

import json
from enum import StrEnum
from typing import Annotated, Any

import typer

from todoist_cli.commands._utils import (
    client_from_context,
    output_options,
    raise_click_error,
)
from todoist_cli.errors import TodoistCLIError
from todoist_cli.output import render_output


class RawMethod(StrEnum):
    get = "GET"
    post = "POST"
    put = "PUT"
    patch = "PATCH"
    delete = "DELETE"


def raw_request(
    ctx: typer.Context,
    method: Annotated[RawMethod, typer.Argument(help="HTTP method.")],
    path: Annotated[str, typer.Argument(help="API path, such as /tasks.")],
    json_body: Annotated[
        str | None,
        typer.Option("--json", help="Raw JSON request body."),
    ] = None,
) -> None:
    """Call an API endpoint without a first-class command."""
    payload: Any | None = None
    if json_body is not None:
        try:
            payload = json.loads(json_body)
        except json.JSONDecodeError as exc:
            raise typer.BadParameter(
                "Value must be valid JSON.",
                param_hint="--json",
            ) from exc

    try:
        data = client_from_context(ctx).request(
            method.value,
            path,
            json=payload,
        )
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, **output_options(ctx))
