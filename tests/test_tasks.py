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
def test_tasks_list_renders_table_and_sends_filters() -> None:
    route = respx.get("https://api.todoist.test/tasks").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": "task-1",
                    "content": "Buy milk",
                    "project_id": "project-1",
                    "due": {"date": "2026-04-20"},
                    "priority": 4,
                    "is_completed": False,
                }
            ],
        )
    )

    result = runner.invoke(
        app,
        command(
            "tasks",
            "list",
            "--project-id",
            "project-1",
            "--section-id",
            "section-1",
            "--label-id",
            "label-1",
            "--filter",
            "today",
            "--ids",
            "task-1,task-2",
        ),
    )

    assert result.exit_code == 0
    assert "Buy milk" in result.output
    request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer test-token"
    assert request.url.params["project_id"] == "project-1"
    assert request.url.params["section_id"] == "section-1"
    assert request.url.params["label_id"] == "label-1"
    assert request.url.params["filter"] == "today"
    assert request.url.params["ids"] == "task-1,task-2"


@respx.mock
def test_tasks_add_sends_payload_and_renders_json() -> None:
    route = respx.post("https://api.todoist.test/tasks").mock(
        return_value=httpx.Response(200, json={"id": "task-1", "content": "Buy milk"})
    )

    result = runner.invoke(
        app,
        command(
            "--format",
            "json",
            "tasks",
            "add",
            "Buy milk",
            "--description",
            "One bottle",
            "--project-id",
            "project-1",
            "--section-id",
            "section-1",
            "--parent-id",
            "parent-1",
            "--label-id",
            "label-1",
            "--label-id",
            "label-2",
            "--due",
            "tomorrow",
            "--priority",
            "4",
        ),
    )

    assert result.exit_code == 0
    assert json.loads(result.output) == {"id": "task-1", "content": "Buy milk"}
    request = route.calls.last.request
    assert request.headers["X-Request-Id"]
    assert json.loads(request.content) == {
        "content": "Buy milk",
        "description": "One bottle",
        "project_id": "project-1",
        "section_id": "section-1",
        "parent_id": "parent-1",
        "label_ids": ["label-1", "label-2"],
        "due_string": "tomorrow",
        "priority": 4,
    }


@respx.mock
def test_tasks_get_renders_single_task() -> None:
    respx.get("https://api.todoist.test/tasks/task-1").mock(
        return_value=httpx.Response(200, json={"id": "task-1", "content": "Buy milk"})
    )

    result = runner.invoke(app, command("tasks", "get", "task-1"))

    assert result.exit_code == 0
    assert "task-1" in result.output
    assert "Buy milk" in result.output


@respx.mock
def test_tasks_update_sends_only_changed_fields() -> None:
    route = respx.post("https://api.todoist.test/tasks/task-1").mock(
        return_value=httpx.Response(
            200,
            json={"id": "task-1", "content": "Buy oat milk"},
        )
    )

    result = runner.invoke(
        app,
        command(
            "tasks",
            "update",
            "task-1",
            "--content",
            "Buy oat milk",
            "--label-id",
            "label-1",
        ),
    )

    assert result.exit_code == 0
    assert "Buy oat milk" in result.output
    assert json.loads(route.calls.last.request.content) == {
        "content": "Buy oat milk",
        "label_ids": ["label-1"],
    }


@respx.mock
def test_task_state_and_delete_commands_render_success() -> None:
    respx.post("https://api.todoist.test/tasks/task-1/close").mock(
        return_value=httpx.Response(204)
    )
    respx.post("https://api.todoist.test/tasks/task-1/reopen").mock(
        return_value=httpx.Response(204)
    )
    respx.delete("https://api.todoist.test/tasks/task-1").mock(
        return_value=httpx.Response(204)
    )

    close = runner.invoke(app, command("tasks", "close", "task-1"))
    reopen = runner.invoke(app, command("tasks", "reopen", "task-1"))
    delete = runner.invoke(app, command("tasks", "delete", "task-1"))

    assert close.exit_code == 0
    assert reopen.exit_code == 0
    assert delete.exit_code == 0
    assert "Done." in close.output
    assert "Done." in reopen.output
    assert "Done." in delete.output
