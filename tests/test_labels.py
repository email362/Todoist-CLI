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
def test_labels_list_renders_table() -> None:
    route = respx.get("https://api.todoist.test/labels").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": "label-1",
                    "name": "Errand",
                    "color": "berry_red",
                    "order": 1,
                    "is_favorite": False,
                }
            ],
        )
    )

    result = runner.invoke(app, command("labels", "list"))

    assert result.exit_code == 0
    assert "Errand" in result.output
    assert route.calls.last.request.headers["Authorization"] == "Bearer test-token"


@respx.mock
def test_labels_add_sends_payload_and_renders_json() -> None:
    route = respx.post("https://api.todoist.test/labels").mock(
        return_value=httpx.Response(
            200,
            json={"id": "label-1", "name": "Errand", "is_favorite": True},
        )
    )

    result = runner.invoke(
        app,
        command(
            "--format",
            "json",
            "labels",
            "add",
            "Errand",
            "--color",
            "berry_red",
            "--order",
            "3",
            "--favorite",
        ),
    )

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "id": "label-1",
        "name": "Errand",
        "is_favorite": True,
    }
    request = route.calls.last.request
    assert request.headers["X-Request-Id"]
    assert json.loads(request.content) == {
        "name": "Errand",
        "color": "berry_red",
        "order": 3,
        "is_favorite": True,
    }


@respx.mock
def test_labels_get_and_update_render_responses() -> None:
    update_route = respx.post("https://api.todoist.test/labels/label-1").mock(
        return_value=httpx.Response(
            200,
            json={"id": "label-1", "name": "Chore", "is_favorite": False},
        )
    )
    respx.get("https://api.todoist.test/labels/label-1").mock(
        return_value=httpx.Response(200, json={"id": "label-1", "name": "Errand"})
    )

    get_result = runner.invoke(app, command("labels", "get", "label-1"))
    update_result = runner.invoke(
        app,
        command(
            "labels",
            "update",
            "label-1",
            "--name",
            "Chore",
            "--order",
            "4",
            "--no-favorite",
        ),
    )

    assert get_result.exit_code == 0
    assert "Errand" in get_result.output
    assert update_result.exit_code == 0
    assert "Chore" in update_result.output
    assert json.loads(update_route.calls.last.request.content) == {
        "name": "Chore",
        "order": 4,
        "is_favorite": False,
    }


@respx.mock
def test_labels_delete_renders_success() -> None:
    respx.delete("https://api.todoist.test/labels/label-1").mock(
        return_value=httpx.Response(204)
    )

    result = runner.invoke(app, command("labels", "delete", "label-1"))

    assert result.exit_code == 0
    assert "Done." in result.output
