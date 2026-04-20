# Todoist CLI

A Python command-line tool for Todoist API operations.

This repository is currently at milestone 3: project skeleton, authentication
configuration, the HTTP client foundation, and first-class task and project
commands.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Usage

```bash
todoist --help
python -m todoist_cli --help
todoist tasks list
todoist tasks add "Buy milk" --due "tomorrow"
todoist projects list
todoist projects add "Shopping List"
```

Authentication precedence:

1. `--token TOKEN`
2. `TODOIST_API_TOKEN` environment variable
3. A stored config file created by `todoist auth login`

The default Todoist API base URL is:

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
intentionally limits resource commands to milestone 3 tasks and projects.
