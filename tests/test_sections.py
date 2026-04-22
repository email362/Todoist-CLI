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
def test_sections_list_sends_project_filter_and_renders_table() -> None:
    route = respx.get("https://api.todoist.test/sections").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": "section-1",
                    "name": "Groceries",
                    "project_id": "project-1",
                    "order": 2,
                }
            ],
        )
    )

    result = runner.invoke(
        app,
        command("sections", "list", "--project-id", "project-1"),
    )

    assert result.exit_code == 0
    assert "Groceries" in result.output
    assert route.calls.last.request.url.params["project_id"] == "project-1"


@respx.mock
def test_sections_list_renders_wrapped_results_payload() -> None:
    respx.get("https://api.todoist.test/sections").mock(
        return_value=httpx.Response(
            200,
            json={
                "results": [
                    {
                        "id": "section-1",
                        "name": "Groceries",
                        "project_id": "project-1",
                        "order": 2,
                    }
                ]
            },
        )
    )

    result = runner.invoke(
        app,
        command("sections", "list", "--project-id", "project-1"),
    )

    assert result.exit_code == 0
    assert "Groceries" in result.output


@respx.mock
def test_sections_add_sends_payload_and_renders_json() -> None:
    route = respx.post("https://api.todoist.test/sections").mock(
        return_value=httpx.Response(
            200,
            json={"id": "section-1", "name": "Groceries", "project_id": "project-1"},
        )
    )

    result = runner.invoke(
        app,
        command(
            "--format",
            "json",
            "sections",
            "add",
            "Groceries",
            "--project-id",
            "project-1",
            "--order",
            "2",
        ),
    )

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "id": "section-1",
        "name": "Groceries",
        "project_id": "project-1",
    }
    request = route.calls.last.request
    assert request.headers["X-Request-Id"]
    assert json.loads(request.content) == {
        "name": "Groceries",
        "project_id": "project-1",
        "order": 2,
    }


@respx.mock
def test_sections_get_and_update_render_responses() -> None:
    update_route = respx.post("https://api.todoist.test/sections/section-1").mock(
        return_value=httpx.Response(
            200,
            json={"id": "section-1", "name": "Market", "project_id": "project-1"},
        )
    )
    respx.get("https://api.todoist.test/sections/section-1").mock(
        return_value=httpx.Response(
            200,
            json={"id": "section-1", "name": "Groceries", "project_id": "project-1"},
        )
    )

    get_result = runner.invoke(app, command("sections", "get", "section-1"))
    update_result = runner.invoke(
        app,
        command("sections", "update", "section-1", "--name", "Market"),
    )

    assert get_result.exit_code == 0
    assert "Groceries" in get_result.output
    assert update_result.exit_code == 0
    assert "Market" in update_result.output
    assert json.loads(update_route.calls.last.request.content) == {"name": "Market"}


@respx.mock
def test_sections_delete_renders_success() -> None:
    respx.delete("https://api.todoist.test/sections/section-1").mock(
        return_value=httpx.Response(204)
    )

    result = runner.invoke(app, command("sections", "delete", "section-1"))

    assert result.exit_code == 0
    assert "Done." in result.output
