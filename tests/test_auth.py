from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from todoist_cli.auth import resolve_token, store_token
from todoist_cli.config import TodoistConfig, load_config, save_config
from todoist_cli.errors import MissingTokenError


def test_token_precedence_option_env_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    save_config(TodoistConfig(token="config-token"), config_path)

    result = resolve_token(
        "option-token",
        environ={"TODOIST_API_TOKEN": "env-token"},
        config_path=config_path,
    )

    assert result.token == "option-token"
    assert result.source == "option"


def test_token_precedence_env_before_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    save_config(TodoistConfig(token="config-token"), config_path)

    result = resolve_token(
        environ={"TODOIST_API_TOKEN": "env-token"},
        config_path=config_path,
    )

    assert result.token == "env-token"
    assert result.source == "environment"


def test_token_precedence_config_last(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    save_config(TodoistConfig(token="config-token"), config_path)

    result = resolve_token(environ={}, config_path=config_path)

    assert result.token == "config-token"
    assert result.source == "config"


def test_missing_token_raises(tmp_path: Path) -> None:
    with pytest.raises(MissingTokenError):
        resolve_token(environ={}, config_path=tmp_path / "missing.toml")


def test_store_token_writes_config_with_private_permissions(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"

    store_token("stored-token", config_path=config_path)

    assert load_config(config_path).token == "stored-token"
    mode = stat.S_IMODE(os.stat(config_path).st_mode)
    assert mode == 0o600
