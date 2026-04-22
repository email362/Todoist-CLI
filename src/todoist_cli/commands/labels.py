from __future__ import annotations

from typing import Annotated

import typer

from todoist_cli.commands._utils import (
    client_from_context,
    compact_dict,
    output_options,
    raise_click_error,
)
from todoist_cli.errors import TodoistCLIError
from todoist_cli.output import Column, render_output

app = typer.Typer(help="Manage Todoist labels.")

LABEL_COLUMNS: list[Column] = [
    ("ID", "id"),
    ("Name", "name"),
    ("Color", "color"),
    ("Order", "order"),
    ("Favorite", "is_favorite"),
]


@app.command("list")
def list_labels(ctx: typer.Context) -> None:
    """List labels."""
    try:
        data = client_from_context(ctx).get("/labels")
    except TodoistCLIError as exc:
        raise_click_error(exc)
    if isinstance(data, dict):
        wrapped_results = data.get("results")
        if isinstance(wrapped_results, list):
            data = wrapped_results
    render_output(data, columns=LABEL_COLUMNS, **output_options(ctx))


@app.command("add")
def add_label(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="Label name.")],
    color: Annotated[
        str | None,
        typer.Option("--color", help="Label color ID or name accepted by Todoist."),
    ] = None,
    order: Annotated[
        int | None,
        typer.Option("--order", help="Label order."),
    ] = None,
    favorite: Annotated[
        bool | None,
        typer.Option("--favorite/--no-favorite", help="Set favorite state."),
    ] = None,
) -> None:
    """Create a label."""
    payload = compact_dict(
        {
            "name": name,
            "color": color,
            "order": order,
            "is_favorite": favorite,
        }
    )
    try:
        data = client_from_context(ctx).post("/labels", json=payload)
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=LABEL_COLUMNS, **output_options(ctx))


@app.command("get")
def get_label(
    ctx: typer.Context,
    label_id: Annotated[str, typer.Argument(help="Label ID.")],
) -> None:
    """Show one label."""
    try:
        data = client_from_context(ctx).get(f"/labels/{label_id}")
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=LABEL_COLUMNS, **output_options(ctx))


@app.command("update")
def update_label(
    ctx: typer.Context,
    label_id: Annotated[str, typer.Argument(help="Label ID.")],
    name: Annotated[
        str | None,
        typer.Option("--name", help="Label name."),
    ] = None,
    color: Annotated[
        str | None,
        typer.Option("--color", help="Label color ID or name accepted by Todoist."),
    ] = None,
    order: Annotated[
        int | None,
        typer.Option("--order", help="Label order."),
    ] = None,
    favorite: Annotated[
        bool | None,
        typer.Option("--favorite/--no-favorite", help="Set favorite state."),
    ] = None,
) -> None:
    """Update a label."""
    payload = compact_dict(
        {
            "name": name,
            "color": color,
            "order": order,
            "is_favorite": favorite,
        }
    )
    try:
        data = client_from_context(ctx).post(f"/labels/{label_id}", json=payload)
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=LABEL_COLUMNS, **output_options(ctx))


@app.command("delete")
def delete_label(
    ctx: typer.Context,
    label_id: Annotated[str, typer.Argument(help="Label ID.")],
) -> None:
    """Delete a label."""
    try:
        data = client_from_context(ctx).delete(f"/labels/{label_id}")
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, **output_options(ctx))
