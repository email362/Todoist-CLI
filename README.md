# Todoist CLI

A Python command-line tool for Todoist API operations.

This repository is currently at milestone 6: project skeleton, authentication
configuration, the HTTP client foundation, first-class task, project, section,
label, and comment commands, thin sync support, a raw API escape hatch, and
release polish documentation.

## Install

Create and activate a virtual environment first:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

For local development:

```bash
python3 -m pip install -e ".[dev]"
```

For normal local use from a checkout:

```bash
python3 -m pip install .
```

The installed console command is:

```bash
todoist --help
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

## Shell Completion

Completion scripts can be installed after the CLI is available on PATH:

```bash
todoist --install-completion bash
todoist --install-completion zsh
todoist --install-completion fish
```

To print a completion script without modifying shell startup files:

```bash
todoist --show-completion bash
```

See [docs/shell-completion.md](docs/shell-completion.md) for shell-specific
notes.

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

## Scripting

For scripts and CI, prefer `TODOIST_API_TOKEN` instead of `todoist auth login`:

```bash
export TODOIST_API_TOKEN="..."
todoist --format json tasks list --filter "today"
```

Use `--format json` when a script needs the full API-shaped response, or
`--format ndjson` for line-oriented processing:

```bash
todoist --format ndjson projects list
```

Example scripts are available in [examples/](examples/):

- [examples/list-today-json.sh](examples/list-today-json.sh) lists today's tasks as JSON.
- [examples/add-tasks-from-lines.sh](examples/add-tasks-from-lines.sh) adds one task per non-empty, non-comment line from a file.

Keep tokens in environment variables or secret managers. Do not hard-code tokens
in scripts.

## Development

```bash
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
make check
```

Individual quality commands:

```bash
make lint
make typecheck
make test
```

Equivalent direct commands are `python3 -m ruff check .`, `python3 -m mypy`,
and `python3 -m pytest`.

## Packaging

Build a source distribution and wheel:

```bash
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
make build
```

Artifacts are written to `dist/`. See [docs/release.md](docs/release.md) for the
release checklist.

## Scope

The planned CLI shape and milestones are tracked in `PLAN.md`. Current code
intentionally stops at milestone 6: documentation, packaging, scripting, and
quality-command polish for the existing command set.
