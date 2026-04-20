from __future__ import annotations

import httpx
import pytest
import respx

from todoist_cli.client import TodoistClient
from todoist_cli.errors import TodoistAPIError, TodoistClientError


@respx.mock
def test_get_sends_auth_header_and_returns_json() -> None:
    route = respx.get("https://api.todoist.test/tasks").mock(
        return_value=httpx.Response(200, json=[{"id": "1", "content": "Buy milk"}])
    )
    client = TodoistClient(token="secret-token", base_url="https://api.todoist.test")

    result = client.get("/tasks", params={"filter": "today"})

    assert result == [{"id": "1", "content": "Buy milk"}]
    request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer secret-token"
    assert "X-Request-Id" not in request.headers
    assert request.url.params["filter"] == "today"


@respx.mock
def test_post_sends_json_and_request_id() -> None:
    route = respx.post("https://api.todoist.test/tasks").mock(
        return_value=httpx.Response(200, json={"id": "1"})
    )
    client = TodoistClient(token="secret-token", base_url="https://api.todoist.test/")

    result = client.post("/tasks", json={"content": "Buy milk"})

    assert result == {"id": "1"}
    request = route.calls.last.request
    assert request.headers["Content-Type"] == "application/json"
    assert request.headers["X-Request-Id"]
    assert request.content == b'{"content":"Buy milk"}'


@respx.mock
def test_204_returns_none() -> None:
    respx.delete("https://api.todoist.test/tasks/1").mock(
        return_value=httpx.Response(204)
    )
    client = TodoistClient(token="secret-token", base_url="https://api.todoist.test")

    assert client.delete("/tasks/1") is None


@respx.mock
def test_api_error_uses_safe_message() -> None:
    respx.get("https://api.todoist.test/tasks").mock(
        return_value=httpx.Response(
            401,
            json={"error": "bad token secret-token"},
            headers={"X-Request-Id": "req-1"},
        )
    )
    client = TodoistClient(token="secret-token", base_url="https://api.todoist.test")

    with pytest.raises(TodoistAPIError) as exc_info:
        client.get("/tasks")

    message = str(exc_info.value)
    assert "secret-token" not in message
    assert "<redacted>" in message
    assert "req-1" in message


@respx.mock
def test_invalid_json_raises_client_error() -> None:
    respx.get("https://api.todoist.test/tasks").mock(
        return_value=httpx.Response(200, text="not json")
    )
    client = TodoistClient(token="secret-token", base_url="https://api.todoist.test")

    with pytest.raises(TodoistClientError):
        client.get("/tasks")
