# Todoist CLI

A Python command-line tool for Todoist API operations.

This repository is currently at milestone 5: project skeleton, authentication
configuration, the HTTP client foundation, first-class task, project, section,
label, and comment commands, plus thin sync support and a raw API escape hatch.

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
todoist sections list --project-id 123
todoist labels list
todoist comments add --task-id 456 "Need one bottle"
todoist sync all
todoist sync resources --types projects,items
todoist raw GET /tasks
todoist raw POST /tasks --json '{"content":"Buy milk"}'
```

Authentication precedence:

1. `--token TOKEN`
2. `TODOIST_API_TOKEN` environment variable
3. A stored config file created by `todoist auth login`

The default Todoist API base URL is:

```text
https://api.todoist.com/api/v1
```

## Sync and Raw Commands

Use first-class resource commands for normal task, project, section, label, and
comment work. They provide stable option names, payload construction, and
readable default output.

Use `todoist sync all` or `todoist sync resources --types TYPE[,TYPE]` when you
need Todoist's Sync API response directly, including `sync_token` handling or
resource types that do not have first-class CLI commands yet. Pass
`--sync-token TOKEN` for incremental sync; the default `*` requests a full sync.

Use `todoist raw METHOD /path` when Todoist exposes an endpoint before this CLI
has a wrapper for it, or when you need to test an API call exactly as documented.
For request bodies, pass raw JSON with `--json`. Prefer the first-class commands
when they exist because raw commands do not validate endpoint-specific fields.

## Development

```bash
pytest
ruff check .
mypy
```

## Scope

The planned CLI shape and milestones are tracked in `PLAN.md`. Current code
intentionally stops at milestone 5: resource commands through comments, thin
sync support, and the raw escape hatch.
