from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from todoist_cli.app import app
from todoist_cli.config import load_config

runner = CliRunner()


def test_auth_login_status_logout_with_isolated_config(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    config_path = tmp_path / "todoist-cli" / "config.toml"

    result = runner.invoke(
        app,
        [
            "--base-url",
            "https://api.todoist.test",
            "auth",
            "login",
        ],
        input="stored-token\n",
    )

    assert result.exit_code == 0
    assert "stored-token" not in result.output
    assert load_config(config_path).token == "stored-token"

    status = runner.invoke(app, ["auth", "status"])
    assert status.exit_code == 0
    assert "config" in status.output

    logout = runner.invoke(app, ["auth", "logout"])
    assert logout.exit_code == 0
    assert not config_path.exists()


def test_auth_status_reports_missing_token(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("TODOIST_API_TOKEN", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    result = runner.invoke(app, ["auth", "status"])

    assert result.exit_code == 1
    assert "No Todoist API token configured." in result.output
