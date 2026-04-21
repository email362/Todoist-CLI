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
def test_raw_get_sends_path_and_renders_table() -> None:
    route = respx.get("https://api.todoist.test/tasks").mock(
        return_value=httpx.Response(
            200,
            json=[{"id": "task-1", "content": "Buy milk"}],
        )
    )

    result = runner.invoke(app, command("raw", "GET", "/tasks"))

    assert result.exit_code == 0
    assert "task-1" in result.output
    assert "Buy milk" in result.output
    assert route.calls.last.request.headers["Authorization"] == "Bearer test-token"


@respx.mock
def test_raw_post_sends_json_body_and_renders_json_response() -> None:
    route = respx.post("https://api.todoist.test/tasks").mock(
        return_value=httpx.Response(
            200,
            json={"id": "task-1", "content": "Buy milk"},
        )
    )

    result = runner.invoke(
        app,
        command(
            "--format",
            "json",
            "raw",
            "POST",
            "/tasks",
            "--json",
            '{"content":"Buy milk"}',
        ),
    )

    assert result.exit_code == 0
    assert json.loads(result.output) == {"id": "task-1", "content": "Buy milk"}
    request = route.calls.last.request
    assert request.headers["Content-Type"] == "application/json"
    assert request.headers["X-Request-Id"]
    assert json.loads(request.content) == {"content": "Buy milk"}


@respx.mock
def test_raw_delete_renders_success_for_empty_response() -> None:
    respx.delete("https://api.todoist.test/tasks/task-1").mock(
        return_value=httpx.Response(204)
    )

    result = runner.invoke(app, command("raw", "DELETE", "/tasks/task-1"))

    assert result.exit_code == 0
    assert "Done." in result.output


def test_raw_json_body_must_be_valid_json() -> None:
    result = runner.invoke(
        app,
        command("raw", "POST", "/tasks", "--json", '{"content":'),
    )

    assert result.exit_code == 2
    assert "valid JSON" in result.output
