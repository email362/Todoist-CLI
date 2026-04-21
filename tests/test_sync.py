from __future__ import annotations

import json
from urllib.parse import parse_qs

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
def test_sync_all_posts_full_sync_request_and_renders_response() -> None:
    route = respx.post("https://api.todoist.test/sync").mock(
        return_value=httpx.Response(
            200,
            json={
                "sync_token": "next-token",
                "full_sync": True,
                "projects": [{"id": "project-1", "name": "Inbox"}],
            },
        )
    )

    result = runner.invoke(app, command("sync", "all"))

    assert result.exit_code == 0
    assert "next-token" in result.output
    assert "Inbox" in result.output
    request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer test-token"
    assert request.headers["X-Request-Id"]
    body = parse_qs(request.content.decode())
    assert body["sync_token"] == ["*"]
    assert json.loads(body["resource_types"][0]) == ["all"]


@respx.mock
def test_sync_resources_posts_selected_types_and_incremental_token() -> None:
    route = respx.post("https://api.todoist.test/sync").mock(
        return_value=httpx.Response(
            200,
            json={"sync_token": "next-token", "full_sync": False, "items": []},
        )
    )

    result = runner.invoke(
        app,
        command(
            "--format",
            "json",
            "sync",
            "resources",
            "--types",
            "projects,items",
            "--sync-token",
            "previous-token",
        ),
    )

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "sync_token": "next-token",
        "full_sync": False,
        "items": [],
    }
    body = parse_qs(route.calls.last.request.content.decode())
    assert body["sync_token"] == ["previous-token"]
    assert json.loads(body["resource_types"][0]) == ["projects", "items"]


def test_sync_resources_requires_at_least_one_type() -> None:
    result = runner.invoke(app, command("sync", "resources", "--types", ","))

    assert result.exit_code == 2
    assert "at least one resource type" in result.output
