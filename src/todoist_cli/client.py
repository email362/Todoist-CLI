from __future__ import annotations

import uuid
from typing import Any

import httpx

from todoist_cli.errors import TodoistAPIError, TodoistClientError, redact


class TodoistClient:
    def __init__(
        self,
        *,
        token: str,
        base_url: str,
        timeout: float = 30.0,
    ) -> None:
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        request_path = path if path.startswith("/") else f"/{path}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        if json is not None:
            headers["Content-Type"] = "application/json"
        if method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
            headers["X-Request-Id"] = str(uuid.uuid4())

        try:
            response = httpx.request(
                method,
                f"{self.base_url}{request_path}",
                params=params,
                json=json,
                headers=headers,
                timeout=self.timeout,
            )
        except httpx.HTTPError as exc:
            message = redact(str(exc), [self.token])
            raise TodoistClientError(message) from exc

        if response.status_code == 204:
            return None

        if response.status_code == 200:
            return _json_response(response, self.token)

        raise TodoistAPIError(
            status_code=response.status_code,
            message=redact(_error_message(response), [self.token]),
            request_id=response.headers.get("X-Request-Id"),
        )

    def get(self, path: str, **kwargs: Any) -> Any:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Any:
        return self.request("POST", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Any:
        return self.request("DELETE", path, **kwargs)


def _json_response(response: httpx.Response, token: str) -> Any:
    try:
        return response.json()
    except ValueError as exc:
        raise TodoistClientError(
            redact("Todoist API returned invalid JSON.", [token])
        ) from exc


def _error_message(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return response.text or response.reason_phrase

    if isinstance(body, dict):
        for key in ("error", "message", "detail"):
            value = body.get(key)
            if isinstance(value, str) and value:
                return value
    return response.text or response.reason_phrase
