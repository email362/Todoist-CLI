from __future__ import annotations

import json

import httpx
import respx
from typer.testing import CliRunner

from todoist_cli.app import app

runner = CliRunner()


def command(*args: str) -> list[str]:
    return [
        "--token",
        "test-token",
        "--base-url",
        "https://api.todoist.test",
        *args,
    ]


@respx.mock
def test_comments_list_sends_task_filter_and_renders_table() -> None:
    route = respx.get("https://api.todoist.test/comments").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": "comment-1",
                    "content": "Need one bottle",
                    "task_id": "task-1",
                    "posted_at": "2026-04-21T12:00:00Z",
                }
            ],
        )
    )

    result = runner.invoke(
        app,
        command("comments", "list", "--task-id", "task-1"),
    )

    assert result.exit_code == 0
    assert "Need one bottle" in result.output
    assert route.calls.last.request.url.params["task_id"] == "task-1"


@respx.mock
def test_comments_list_sends_project_filter() -> None:
    route = respx.get("https://api.todoist.test/comments").mock(
        return_value=httpx.Response(200, json=[]),
    )

    result = runner.invoke(
        app,
        command("comments", "list", "--project-id", "project-1"),
    )

    assert result.exit_code == 0
    assert "No results." in result.output
    assert route.calls.last.request.url.params["project_id"] == "project-1"


@respx.mock
def test_comments_add_sends_payload_and_renders_json() -> None:
    route = respx.post("https://api.todoist.test/comments").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "comment-1",
                "content": "Need one bottle",
                "task_id": "task-1",
            },
        )
    )

    result = runner.invoke(
        app,
        command(
            "--format",
            "json",
            "comments",
            "add",
            "Need one bottle",
            "--task-id",
            "task-1",
        ),
    )

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "id": "comment-1",
        "content": "Need one bottle",
        "task_id": "task-1",
    }
    request = route.calls.last.request
    assert request.headers["X-Request-Id"]
    assert json.loads(request.content) == {
        "content": "Need one bottle",
        "task_id": "task-1",
    }


@respx.mock
def test_comments_get_and_update_render_responses() -> None:
    update_route = respx.post("https://api.todoist.test/comments/comment-1").mock(
        return_value=httpx.Response(
            200,
            json={"id": "comment-1", "content": "Need two bottles"},
        )
    )
    respx.get("https://api.todoist.test/comments/comment-1").mock(
        return_value=httpx.Response(
            200,
            json={"id": "comment-1", "content": "Need one bottle"},
        )
    )

    get_result = runner.invoke(app, command("comments", "get", "comment-1"))
    update_result = runner.invoke(
        app,
        command(
            "comments",
            "update",
            "comment-1",
            "--content",
            "Need two bottles",
        ),
    )

    assert get_result.exit_code == 0
    assert "Need one bottle" in get_result.output
    assert update_result.exit_code == 0
    assert "Need two bottles" in update_result.output
    assert json.loads(update_route.calls.last.request.content) == {
        "content": "Need two bottles"
    }


def test_comments_list_requires_exactly_one_target() -> None:
    missing = runner.invoke(app, command("comments", "list"))
    duplicate = runner.invoke(
        app,
        command("comments", "list", "--task-id", "task-1", "--project-id", "project-1"),
    )

    assert missing.exit_code == 2
    assert duplicate.exit_code == 2
    assert "exactly one" in missing.output
    assert "exactly one" in duplicate.output


@respx.mock
def test_comments_delete_renders_success() -> None:
    respx.delete("https://api.todoist.test/comments/comment-1").mock(
        return_value=httpx.Response(204)
    )

    result = runner.invoke(app, command("comments", "delete", "comment-1"))

    assert result.exit_code == 0
    assert "Done." in result.output
