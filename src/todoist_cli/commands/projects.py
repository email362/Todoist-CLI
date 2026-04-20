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

app = typer.Typer(help="Manage Todoist projects.")

PROJECT_COLUMNS: list[Column] = [
    ("ID", "id"),
    ("Name", "name"),
    ("Color", "color"),
    ("Favorite", "is_favorite"),
]


@app.command("list")
def list_projects(ctx: typer.Context) -> None:
    """List projects."""
    try:
        data = client_from_context(ctx).get("/projects")
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=PROJECT_COLUMNS, **output_options(ctx))


@app.command("add")
def add_project(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="Project name.")],
    color: Annotated[
        str | None,
        typer.Option("--color", help="Project color ID or name accepted by Todoist."),
    ] = None,
    favorite: Annotated[
        bool | None,
        typer.Option("--favorite/--no-favorite", help="Set favorite state."),
    ] = None,
) -> None:
    """Create a project."""
    payload = compact_dict(
        {
            "name": name,
            "color": color,
            "is_favorite": favorite,
        }
    )
    try:
        data = client_from_context(ctx).post("/projects", json=payload)
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=PROJECT_COLUMNS, **output_options(ctx))


@app.command("get")
def get_project(
    ctx: typer.Context,
    project_id: Annotated[str, typer.Argument(help="Project ID.")],
) -> None:
    """Show one project."""
    try:
        data = client_from_context(ctx).get(f"/projects/{project_id}")
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=PROJECT_COLUMNS, **output_options(ctx))


@app.command("update")
def update_project(
    ctx: typer.Context,
    project_id: Annotated[str, typer.Argument(help="Project ID.")],
    name: Annotated[
        str | None,
        typer.Option("--name", help="Project name."),
    ] = None,
    color: Annotated[
        str | None,
        typer.Option("--color", help="Project color ID or name accepted by Todoist."),
    ] = None,
    favorite: Annotated[
        bool | None,
        typer.Option("--favorite/--no-favorite", help="Set favorite state."),
    ] = None,
) -> None:
    """Update a project."""
    payload = compact_dict(
        {
            "name": name,
            "color": color,
            "is_favorite": favorite,
        }
    )
    try:
        data = client_from_context(ctx).post(f"/projects/{project_id}", json=payload)
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=PROJECT_COLUMNS, **output_options(ctx))


@app.command("delete")
def delete_project(
    ctx: typer.Context,
    project_id: Annotated[str, typer.Argument(help="Project ID.")],
) -> None:
    """Delete a project."""
    try:
        data = client_from_context(ctx).delete(f"/projects/{project_id}")
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, **output_options(ctx))
