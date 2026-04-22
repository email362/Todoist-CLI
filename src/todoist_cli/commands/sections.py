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

app = typer.Typer(help="Manage Todoist sections.")

SECTION_COLUMNS: list[Column] = [
    ("ID", "id"),
    ("Name", "name"),
    ("Project", "project_id"),
    ("Order", "order"),
]


@app.command("list")
def list_sections(
    ctx: typer.Context,
    project_id: Annotated[str, typer.Option("--project-id", help="Project ID.")],
) -> None:
    """List sections in a project."""
    try:
        data = client_from_context(ctx).get(
            "/sections",
            params={"project_id": project_id},
        )
    except TodoistCLIError as exc:
        raise_click_error(exc)
    if isinstance(data, dict):
        wrapped_results = data.get("results")
        if isinstance(wrapped_results, list):
            data = wrapped_results
    render_output(data, columns=SECTION_COLUMNS, **output_options(ctx))


@app.command("add")
def add_section(
    ctx: typer.Context,
    name: Annotated[str, typer.Argument(help="Section name.")],
    project_id: Annotated[str, typer.Option("--project-id", help="Project ID.")],
    order: Annotated[
        int | None,
        typer.Option("--order", help="Section order."),
    ] = None,
) -> None:
    """Create a section."""
    payload = compact_dict(
        {
            "name": name,
            "project_id": project_id,
            "order": order,
        }
    )
    try:
        data = client_from_context(ctx).post("/sections", json=payload)
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=SECTION_COLUMNS, **output_options(ctx))


@app.command("get")
def get_section(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Argument(help="Section ID.")],
) -> None:
    """Show one section."""
    try:
        data = client_from_context(ctx).get(f"/sections/{section_id}")
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=SECTION_COLUMNS, **output_options(ctx))


@app.command("update")
def update_section(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Argument(help="Section ID.")],
    name: Annotated[str, typer.Option("--name", help="Section name.")],
) -> None:
    """Update a section."""
    try:
        data = client_from_context(ctx).post(
            f"/sections/{section_id}",
            json={"name": name},
        )
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=SECTION_COLUMNS, **output_options(ctx))


@app.command("delete")
def delete_section(
    ctx: typer.Context,
    section_id: Annotated[str, typer.Argument(help="Section ID.")],
) -> None:
    """Delete a section."""
    try:
        data = client_from_context(ctx).delete(f"/sections/{section_id}")
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, **output_options(ctx))
