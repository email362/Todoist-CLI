from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir

DEFAULT_CONFIG_DIR_NAME = "todoist-cli"
DEFAULT_CONFIG_FILE_NAME = "config.toml"


@dataclass(slots=True)
class TodoistConfig:
    token: str | None = None
    base_url: str | None = None
    default_format: str | None = None


def default_config_path() -> Path:
    return Path(user_config_dir(DEFAULT_CONFIG_DIR_NAME)) / DEFAULT_CONFIG_FILE_NAME


def load_config(path: Path | None = None) -> TodoistConfig:
    config_path = path or default_config_path()
    if not config_path.exists():
        return TodoistConfig()

    with config_path.open("rb") as file:
        raw = tomllib.load(file)

    return TodoistConfig(
        token=_optional_string(raw.get("token")),
        base_url=_optional_string(raw.get("base_url")),
        default_format=_optional_string(raw.get("default_format")),
    )


def save_config(config: TodoistConfig, path: Path | None = None) -> Path:
    config_path = path or default_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    if config.token is not None:
        lines.append(f'token = "{_escape_toml_string(config.token)}"')
    if config.base_url is not None:
        lines.append(f'base_url = "{_escape_toml_string(config.base_url)}"')
    if config.default_format is not None:
        lines.append(f'default_format = "{_escape_toml_string(config.default_format)}"')

    config_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    os.chmod(config_path, 0o600)
    return config_path


def delete_config(path: Path | None = None) -> bool:
    config_path = path or default_config_path()
    if not config_path.exists():
        return False
    config_path.unlink()
    return True


def _optional_string(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _escape_toml_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
