from __future__ import annotations

from typing import Annotated

import click
import typer

from todoist_cli.commands._utils import (
    client_from_context,
    compact_dict,
    output_options,
    raise_click_error,
)
from todoist_cli.errors import TodoistCLIError
from todoist_cli.output import Column, render_output

app = typer.Typer(help="Manage Todoist comments.")

COMMENT_COLUMNS: list[Column] = [
    ("ID", "id"),
    ("Content", "content"),
    ("Task", "task_id"),
    ("Project", "project_id"),
    ("Posted", "posted_at"),
]


@app.command("list")
def list_comments(
    ctx: typer.Context,
    task_id: Annotated[
        str | None,
        typer.Option("--task-id", help="Task ID."),
    ] = None,
    project_id: Annotated[
        str | None,
        typer.Option("--project-id", help="Project ID."),
    ] = None,
) -> None:
    """List comments for a task or project."""
    params = _target_payload(task_id=task_id, project_id=project_id)
    try:
        data = client_from_context(ctx).get("/comments", params=params)
    except TodoistCLIError as exc:
        raise_click_error(exc)
    if isinstance(data, dict):
        wrapped_results = data.get("results")
        if isinstance(wrapped_results, list):
            data = wrapped_results
    render_output(data, columns=COMMENT_COLUMNS, **output_options(ctx))


@app.command("add")
def add_comment(
    ctx: typer.Context,
    content: Annotated[str, typer.Argument(help="Comment content.")],
    task_id: Annotated[
        str | None,
        typer.Option("--task-id", help="Task ID."),
    ] = None,
    project_id: Annotated[
        str | None,
        typer.Option("--project-id", help="Project ID."),
    ] = None,
) -> None:
    """Create a comment for a task or project."""
    payload = {
        "content": content,
        **_target_payload(task_id=task_id, project_id=project_id),
    }
    try:
        data = client_from_context(ctx).post("/comments", json=payload)
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=COMMENT_COLUMNS, **output_options(ctx))


@app.command("get")
def get_comment(
    ctx: typer.Context,
    comment_id: Annotated[str, typer.Argument(help="Comment ID.")],
) -> None:
    """Show one comment."""
    try:
        data = client_from_context(ctx).get(f"/comments/{comment_id}")
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=COMMENT_COLUMNS, **output_options(ctx))


@app.command("update")
def update_comment(
    ctx: typer.Context,
    comment_id: Annotated[str, typer.Argument(help="Comment ID.")],
    content: Annotated[str, typer.Option("--content", help="Comment content.")],
) -> None:
    """Update a comment."""
    try:
        data = client_from_context(ctx).post(
            f"/comments/{comment_id}",
            json={"content": content},
        )
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, columns=COMMENT_COLUMNS, **output_options(ctx))


@app.command("delete")
def delete_comment(
    ctx: typer.Context,
    comment_id: Annotated[str, typer.Argument(help="Comment ID.")],
) -> None:
    """Delete a comment."""
    try:
        data = client_from_context(ctx).delete(f"/comments/{comment_id}")
    except TodoistCLIError as exc:
        raise_click_error(exc)
    render_output(data, **output_options(ctx))


def _target_payload(*, task_id: str | None, project_id: str | None) -> dict[str, str]:
    payload = compact_dict({"task_id": task_id, "project_id": project_id})
    if len(payload) != 1:
        raise click.UsageError("Provide exactly one of --task-id or --project-id.")
    return payload
