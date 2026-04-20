# Todoist CLI

A Python command-line tool for Todoist API operations.

This repository is currently at milestone 2: project skeleton, authentication
configuration, and the HTTP client foundation. Resource commands are not
implemented yet.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Usage

```bash
todoist --help
python -m todoist_cli --help
```

Planned authentication precedence:

1. `--token TOKEN`
2. `TODOIST_API_TOKEN` environment variable
3. A stored config file created by `todoist auth login`

The planned default Todoist API base URL is:

```text
https://api.todoist.com/api/v1
```

## Development

```bash
pytest
ruff check .
mypy
```

## Scope

The planned CLI shape and milestones are tracked in `PLAN.md`. Current code
intentionally avoids resource commands until later milestones.
