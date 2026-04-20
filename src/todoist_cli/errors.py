from __future__ import annotations

from dataclasses import dataclass

REDACTION = "<redacted>"


def redact(value: str, secrets: list[str | None] | tuple[str | None, ...]) -> str:
    """Replace configured secret values in user-facing text."""
    redacted = value
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, REDACTION)
    return redacted


class TodoistCLIError(Exception):
    """Base exception for concise CLI-safe failures."""

    exit_code = 1


class MissingTokenError(TodoistCLIError):
    """Raised when no Todoist API token can be found."""

    def __init__(self) -> None:
        super().__init__(
            "Todoist API token not found. Pass --token, set TODOIST_API_TOKEN, "
            "or run `todoist auth login`."
        )


@dataclass(slots=True)
class TodoistAPIError(TodoistCLIError):
    status_code: int
    message: str
    request_id: str | None = None

    def __str__(self) -> str:
        suffix = f" (request id: {self.request_id})" if self.request_id else ""
        return f"Todoist API error {self.status_code}: {self.message}{suffix}"


class TodoistClientError(TodoistCLIError):
    """Raised for local client or transport failures."""
