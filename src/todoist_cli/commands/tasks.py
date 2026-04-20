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

app = typer.Typer(help="Manage Todoist tasks.")

TASK_COLUMNS: list[Column] = [
    ("ID", "id"),
    ("Content", "content"),
    ("Project", "project_id"),
    ("Due", "due"),
    ("Priority", "priority"),
    ("Completed", "is_completed"),
]


@app.command("list")
def list_tasks(
    ctx: typer.Context,
    project_id: Annotated[
        str | None,
        typer.Option("--project-id", help="Filter by project ID."),
    ] = None,
    section_id: Annotated[
        str | None,
        typer.Option("--section-id", help="Filter by section ID."),
    ] = None,
    label_id: Annotated[
        str | None,
        typer.Option("--label-id", help="Filter by label ID."),
    ] = None,
    filter_text: Annotated[
        str | None,
        typer.Option("--filter", help="Todoist filter query."),
    ] = None,
    ids: Annotated[
        str | None,
        typer.Option("--ids", help="Comma-separated task IDs."),
    ] = None,
) -> None:
    """List active tasks."""
    params = compact_dict(
        {
            "project_id": project_id,
            "section_id": section_id,
            "label_id": label_id,
            "filter": filter_text,
            "ids": ids,
        }
    )
    try:
        data = client_from_context(ctx).get("/tasks", params=params)
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=TASK_COLUMNS, **output_options(ctx))


@app.command("add")
def add_task(
    ctx: typer.Context,
    content: Annotated[str, typer.Argument(help="Task content.")],
    description: Annotated[
        str | None,
        typer.Option("--description", help="Task description."),
    ] = None,
    project_id: Annotated[
        str | None,
        typer.Option("--project-id", help="Project ID."),
    ] = None,
    section_id: Annotated[
        str | None,
        typer.Option("--section-id", help="Section ID."),
    ] = None,
    parent_id: Annotated[
        str | None,
        typer.Option("--parent-id", help="Parent task ID."),
    ] = None,
    label_ids: Annotated[
        list[str] | None,
        typer.Option("--label-id", help="Label ID. Can be used multiple times."),
    ] = None,
    due: Annotated[
        str | None,
        typer.Option("--due", help="Natural-language due date."),
    ] = None,
    priority: Annotated[
        int | None,
        typer.Option("--priority", min=1, max=4, help="Priority from 1 to 4."),
    ] = None,
) -> None:
    """Create a task."""
    payload = compact_dict(
        {
            "content": content,
            "description": description,
            "project_id": project_id,
            "section_id": section_id,
            "parent_id": parent_id,
            "label_ids": label_ids or None,
            "due_string": due,
            "priority": priority,
        }
    )
    try:
        data = client_from_context(ctx).post("/tasks", json=payload)
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=TASK_COLUMNS, **output_options(ctx))


@app.command("get")
def get_task(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help="Task ID.")],
) -> None:
    """Show one task."""
    try:
        data = client_from_context(ctx).get(f"/tasks/{task_id}")
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=TASK_COLUMNS, **output_options(ctx))


@app.command("update")
def update_task(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help="Task ID.")],
    content: Annotated[
        str | None,
        typer.Option("--content", help="Task content."),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option("--description", help="Task description."),
    ] = None,
    due: Annotated[
        str | None,
        typer.Option("--due", help="Natural-language due date."),
    ] = None,
    priority: Annotated[
        int | None,
        typer.Option("--priority", min=1, max=4, help="Priority from 1 to 4."),
    ] = None,
    label_ids: Annotated[
        list[str] | None,
        typer.Option("--label-id", help="Label ID. Can be used multiple times."),
    ] = None,
) -> None:
    """Update a task."""
    payload = compact_dict(
        {
            "content": content,
            "description": description,
            "due_string": due,
            "priority": priority,
            "label_ids": label_ids or None,
        }
    )
    try:
        data = client_from_context(ctx).post(f"/tasks/{task_id}", json=payload)
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=TASK_COLUMNS, **output_options(ctx))


@app.command("close")
def close_task(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help="Task ID.")],
) -> None:
    """Close a task."""
    try:
        data = client_from_context(ctx).post(f"/tasks/{task_id}/close")
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, **output_options(ctx))


@app.command("reopen")
def reopen_task(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help="Task ID.")],
) -> None:
    """Reopen a task."""
    try:
        data = client_from_context(ctx).post(f"/tasks/{task_id}/reopen")
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, **output_options(ctx))


@app.command("delete")
def delete_task(
    ctx: typer.Context,
    task_id: Annotated[str, typer.Argument(help="Task ID.")],
) -> None:
    """Delete a task."""
    try:
        data = client_from_context(ctx).delete(f"/tasks/{task_id}")
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, **output_options(ctx))
