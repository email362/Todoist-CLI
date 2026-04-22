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
def test_projects_list_renders_json() -> None:
    route = respx.get("https://api.todoist.test/projects").mock(
        return_value=httpx.Response(
            200,
            json=[{"id": "project-1", "name": "Shopping", "is_favorite": False}],
        )
    )

    result = runner.invoke(
        app,
        command("--format", "json", "projects", "list"),
    )

    assert result.exit_code == 0
    assert json.loads(result.output) == [
        {"id": "project-1", "name": "Shopping", "is_favorite": False}
    ]
    assert route.calls.last.request.headers["Authorization"] == "Bearer test-token"


@respx.mock
def test_projects_list_renders_wrapped_results_payload() -> None:
    respx.get("https://api.todoist.test/projects").mock(
        return_value=httpx.Response(
            200,
            json={
                "results": [
                    {"id": "project-1", "name": "Shopping", "is_favorite": False}
                ]
            },
        )
    )

    result = runner.invoke(app, command("projects", "list"))

    assert result.exit_code == 0
    assert "Shopping" in result.output


@respx.mock
def test_projects_add_sends_payload_and_renders_table() -> None:
    route = respx.post("https://api.todoist.test/projects").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "project-1",
                "name": "Shopping",
                "color": "berry_red",
                "is_favorite": True,
            },
        )
    )

    result = runner.invoke(
        app,
        command(
            "projects",
            "add",
            "Shopping",
            "--color",
            "berry_red",
            "--favorite",
        ),
    )

    assert result.exit_code == 0
    assert "Shopping" in result.output
    request = route.calls.last.request
    assert request.headers["X-Request-Id"]
    assert json.loads(request.content) == {
        "name": "Shopping",
        "color": "berry_red",
        "is_favorite": True,
    }


@respx.mock
def test_projects_get_renders_single_project() -> None:
    respx.get("https://api.todoist.test/projects/project-1").mock(
        return_value=httpx.Response(200, json={"id": "project-1", "name": "Shopping"})
    )

    result = runner.invoke(app, command("projects", "get", "project-1"))

    assert result.exit_code == 0
    assert "project-1" in result.output
    assert "Shopping" in result.output


@respx.mock
def test_projects_update_sends_only_changed_fields() -> None:
    route = respx.post("https://api.todoist.test/projects/project-1").mock(
        return_value=httpx.Response(
            200,
            json={"id": "project-1", "name": "Errands", "is_favorite": False},
        )
    )

    result = runner.invoke(
        app,
        command(
            "projects",
            "update",
            "project-1",
            "--name",
            "Errands",
            "--no-favorite",
        ),
    )

    assert result.exit_code == 0
    assert "Errands" in result.output
    assert json.loads(route.calls.last.request.content) == {
        "name": "Errands",
        "is_favorite": False,
    }


@respx.mock
def test_projects_delete_renders_success() -> None:
    respx.delete("https://api.todoist.test/projects/project-1").mock(
        return_value=httpx.Response(204)
    )

    result = runner.invoke(app, command("projects", "delete", "project-1"))

    assert result.exit_code == 0
    assert "Done." in result.output
