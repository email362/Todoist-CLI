from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from todoist_cli.config import load_config, save_config
from todoist_cli.errors import MissingTokenError

TOKEN_ENV_VAR = "TODOIST_API_TOKEN"


@dataclass(frozen=True, slots=True)
class ResolvedToken:
    token: str
    source: str


def resolve_token(
    explicit_token: str | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    config_path: Path | None = None,
) -> ResolvedToken:
    if explicit_token:
        return ResolvedToken(explicit_token, "option")

    env = environ or os.environ
    env_token = env.get(TOKEN_ENV_VAR)
    if env_token:
        return ResolvedToken(env_token, "environment")

    config = load_config(config_path)
    if config.token:
        return ResolvedToken(config.token, "config")

    raise MissingTokenError()


def store_token(
    token: str,
    *,
    config_path: Path | None = None,
    base_url: str | None = None,
    default_format: str | None = None,
) -> Path:
    config = load_config(config_path)
    config.token = token
    if base_url is not None:
        config.base_url = base_url
    if default_format is not None:
        config.default_format = default_format
    return save_config(config, config_path)


def has_stored_token(config_path: Path | None = None) -> bool:
    return bool(load_config(config_path).token)


def resolved_token_status(
    explicit_token: str | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    config_path: Path | None = None,
) -> str | None:
    try:
        return resolve_token(
            explicit_token,
            environ=environ,
            config_path=config_path,
        ).source
    except MissingTokenError:
        return None
