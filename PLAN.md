# Todoist CLI Implementation Plan

## Goal

Build a Python command-line tool that exposes Todoist API operations as CLI commands, using a user-provided Todoist API token.

The CLI should be modeled after Todoist's public API resources and actions so commands map predictably to API concepts:

- `tasks`
- `projects`
- `sections`
- `labels`
- `comments`
- `sync`

Target the current Todoist API v1 docs at `https://developer.todoist.com/api/v1/`. Avoid building against the deprecated REST API v2 docs unless compatibility is explicitly required later.

## User Experience

Installable command:

```bash
todoist --help
```

Authentication options, in precedence order:

1. `--token TOKEN`
2. `TODOIST_API_TOKEN` environment variable
3. Stored config file created by `todoist auth login`

Example commands:

```bash
todoist auth login
todoist tasks list
todoist tasks add "Buy milk" --due "tomorrow" --priority 4
todoist tasks get 2995104339
todoist tasks update 2995104339 --content "Buy oat milk"
todoist tasks close 2995104339
todoist projects list
todoist projects add "Shopping List"
todoist labels list
todoist comments add --task-id 2995104339 "Need one bottle"
todoist raw GET /tasks
```

## Recommended Stack

- Python 3.11+
- `typer` for CLI structure and help text
- `httpx` for HTTP client behavior
- `pydantic` for request and response models where helpful
- `rich` for table, JSON, and error output
- `platformdirs` for config path discovery
- `pytest`, `respx`, and `pytest-cov` for tests
- `ruff` and `mypy` for linting and type checks

Package metadata should live in `pyproject.toml`.

## Repository Layout

```text
todoist-cli/
  pyproject.toml
  README.md
  PLAN.md
  src/
    todoist_cli/
      __init__.py
      __main__.py
      app.py
      auth.py
      client.py
      config.py
      errors.py
      output.py
      models/
        __init__.py
        task.py
        project.py
        section.py
        label.py
        comment.py
      commands/
        __init__.py
        auth.py
        tasks.py
        projects.py
        sections.py
        labels.py
        comments.py
        sync.py
        raw.py
  tests/
    test_auth.py
    test_client.py
    test_tasks.py
    test_projects.py
```

## CLI Shape

Use noun-first command groups to mirror Todoist resources.

### Global Options

```bash
todoist --token TOKEN --format table --verbose tasks list
```

Options:

- `--token`: override configured token
- `--format`: `table`, `json`, or `ndjson`
- `--base-url`: default to `https://api.todoist.com/api/v1`
- `--verbose`: include HTTP and stack details for debugging
- `--no-color`: disable rich formatting

### Auth Commands

```bash
todoist auth login
todoist auth status
todoist auth logout
```

Implementation notes:

- `login` prompts for a token with hidden input.
- Store token in a config file with `0600` permissions.
- Prefer environment variable auth for scripts and CI.
- Do not print tokens in logs, errors, or config dumps.

### Task Commands

```bash
todoist tasks list [--project-id ID] [--section-id ID] [--label-id ID] [--filter TEXT] [--ids ID,ID]
todoist tasks add CONTENT [--description TEXT] [--project-id ID] [--section-id ID] [--parent-id ID] [--label-id ID]... [--due TEXT] [--priority N]
todoist tasks get TASK_ID
todoist tasks update TASK_ID [--content TEXT] [--description TEXT] [--due TEXT] [--priority N] [--label-id ID]...
todoist tasks close TASK_ID
todoist tasks reopen TASK_ID
todoist tasks delete TASK_ID
```

Map these to Todoist task endpoints and preserve API naming where it helps scriptability. Convert CLI kebab-case options to API snake_case fields.

### Project Commands

```bash
todoist projects list
todoist projects add NAME [--color N] [--favorite/--no-favorite]
todoist projects get PROJECT_ID
todoist projects update PROJECT_ID [--name TEXT] [--color N] [--favorite/--no-favorite]
todoist projects delete PROJECT_ID
```

### Section Commands

```bash
todoist sections list --project-id PROJECT_ID
todoist sections add NAME --project-id PROJECT_ID [--order N]
todoist sections get SECTION_ID
todoist sections update SECTION_ID --name NAME
todoist sections delete SECTION_ID
```

### Label Commands

```bash
todoist labels list
todoist labels add NAME [--color N] [--order N] [--favorite/--no-favorite]
todoist labels get LABEL_ID
todoist labels update LABEL_ID [--name TEXT] [--color N] [--order N] [--favorite/--no-favorite]
todoist labels delete LABEL_ID
```

### Comment Commands

```bash
todoist comments list (--task-id TASK_ID | --project-id PROJECT_ID)
todoist comments add CONTENT (--task-id TASK_ID | --project-id PROJECT_ID)
todoist comments get COMMENT_ID
todoist comments update COMMENT_ID --content TEXT
todoist comments delete COMMENT_ID
```

### Sync Commands

```bash
todoist sync all
todoist sync resources --types all
```

Keep sync support thin at first. It is useful for advanced users, but the normal CLI should stay resource-command driven.

### Raw Escape Hatch

```bash
todoist raw GET /tasks
todoist raw POST /tasks --json '{"content":"Buy milk"}'
```

This makes the CLI useful before every endpoint has a first-class wrapper.

## HTTP Client Design

Create one small `TodoistClient` abstraction:

- Holds `base_url`, `token`, timeout, and output-safe request metadata.
- Adds `Authorization: Bearer <token>`.
- Sends JSON bodies with `Content-Type: application/json`.
- Adds `X-Request-Id` for mutating requests by default.
- Handles `200`, `204`, and JSON response parsing.
- Converts API errors into typed exceptions with concise CLI messages.

Suggested methods:

```python
class TodoistClient:
    def request(self, method: str, path: str, *, params: dict | None = None, json: dict | None = None) -> Any: ...
    def get(self, path: str, **kwargs: Any) -> Any: ...
    def post(self, path: str, **kwargs: Any) -> Any: ...
    def delete(self, path: str, **kwargs: Any) -> Any: ...
```

Do not hide the API too aggressively. Command modules can call clear paths like `client.get("/tasks", params=params)`.

## Output Design

Default output should be human-readable tables for list commands and compact key-value detail for single objects.

Machine-readable output:

```bash
todoist --format json tasks list
todoist --format ndjson tasks list
```

Rules:

- JSON output should be raw API-shaped data.
- Table output can rename columns for readability.
- Exit code `0` for success.
- Exit code `1` for API/client errors.
- Exit code `2` for invalid CLI usage.

## Configuration

Config path:

```text
~/.config/todoist-cli/config.toml
```

Example:

```toml
token = "..."
base_url = "https://api.todoist.com/api/v1"
default_format = "table"
```

Token handling:

- Never commit real tokens.
- Add `.env`, config files, and test secrets to `.gitignore`.
- Redact token values in all exception and debug output.

## Testing Plan

Unit tests:

- Token precedence and missing-token errors
- Config read/write and permission handling
- Client request construction
- Error translation
- CLI argument-to-payload conversion

HTTP tests:

- Mock Todoist endpoints with `respx`
- Verify auth header is sent
- Verify mutating requests include `X-Request-Id`
- Verify `204 No Content` becomes success output

CLI tests:

- Use Typer's `CliRunner`
- Cover representative commands:
  - `tasks list`
  - `tasks add`
  - `tasks close`
  - `projects list`
  - `raw GET /tasks`

Manual smoke tests:

```bash
export TODOIST_API_TOKEN=...
todoist --format json projects list
todoist tasks add "CLI smoke test" --due "today"
todoist tasks list --filter "today"
```

## Milestones

### Milestone 1: Project Skeleton

- Add `pyproject.toml`
- Add package under `src/todoist_cli`
- Add Typer app with global options
- Add README with install and auth instructions
- Add basic test/lint commands

### Milestone 2: Auth and Client

- Implement token discovery
- Implement config file auth
- Implement `TodoistClient`
- Add structured errors and redaction
- Add mocked HTTP tests

### Milestone 3: Tasks and Projects

- Implement `tasks list/add/get/update/close/reopen/delete`
- Implement `projects list/add/get/update/delete`
- Add table and JSON output
- Add CLI tests for common flows

### Milestone 4: Sections, Labels, Comments

- Implement section commands
- Implement label commands
- Implement comment commands
- Add tests for command payloads and response rendering

### Milestone 5: Sync and Raw

- Implement thin `sync` command support
- Implement `raw` escape hatch
- Document when to use raw commands

### Milestone 6: Polish

- Add shell completion docs
- Add packaging instructions
- Add examples for scripting
- Run lint, type check, and tests
- Tag first usable release

## Open Decisions

- Whether to depend on Todoist's official Python SDK or call the HTTP API directly.
  - Recommendation: call HTTP directly so CLI command names and payloads can mirror the API exactly.
- Whether destructive commands should require confirmation.
  - Recommendation: prompt by default for deletes unless `--yes` is passed.
- Whether to support OAuth.
  - Recommendation: start with API token support only; add OAuth later if distributing to other users.
- Whether IDs should be parsed as integers or strings.
  - Recommendation: accept strings at the CLI boundary and let JSON payload construction preserve the API's expected shape per endpoint.

## Source References

- Todoist API v1 overview: `https://developer.todoist.com/api/v1/`
- Todoist REST API v1 reference: `https://developer.todoist.com/rest/v1/`
- Deprecated Todoist REST API v2 reference: `https://developer.todoist.com/rest/v2/`
