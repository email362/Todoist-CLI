---
name: todoist-cli
description: Install and use the Todoist CLI to authenticate, inspect, and manage tasks, projects, sections, labels, and comments when a request needs Todoist account access.
---

# Todoist CLI

Use this skill when a task requires the `todoist` command from this repository.
Use the user's request to determine which account data to read or change. The
write commands below are syntax examples, not installation tests.

## Find or install the CLI

Check that `todoist` is available and starts. Its help should show the `tasks`
and `projects` command groups.

```bash
command -v todoist
todoist --help
```

If the command is missing or broken, locate a checkout of this repository. If
none exists, clone it from a directory where the checkout belongs:

```bash
git clone https://github.com/email362/Todoist-CLI.git todoist-cli
cd todoist-cli
```

Use an authenticated Git remote if the HTTPS URL is unavailable. The CLI
requires Python 3.11 or newer.

From the repository root, install the command in an isolated environment:

```bash
uv tool install .
```

If `uv` is unavailable, use `pipx install .` instead. For a broken `uv` install,
run `uv tool install --force .` from the repository root. If the new executable
is not on `PATH`, run `uv tool update-shell` or `pipx ensurepath`, as appropriate,
then open a new shell. Confirm with `todoist --version` and `todoist --help`.

## Authenticate and verify access

```bash
todoist auth status
todoist projects list
```

`auth status` checks for a token; the read-only projects request checks whether
Todoist accepts it. If the token is missing, have the user run `todoist auth
login` in their terminal, or use an existing `TODOIST_API_TOKEN` supplied through
a secure environment. Do not put a token in a command argument, transcript, or
log. The CLI resolves a token in this order: `--token`, `TODOIST_API_TOKEN`, then
its stored config. `auth login` writes to the user config directory.

## Read account data

```bash
todoist projects list
todoist sections list --project-id PROJECT_ID
todoist tasks list
todoist tasks list --project-id PROJECT_ID
todoist tasks list --filter-query "today"
todoist tasks get TASK_ID
todoist labels list
todoist comments list --task-id TASK_ID
```

Read the relevant list before using an ID in a later command. Put global options
before the command group. For scripts, use `todoist --format json tasks list` or
`todoist --format ndjson projects list`. Run `todoist --help` or
`todoist <group> <command> --help` for current flags and required arguments.

## Change account data

Use the exact target and scope authorized by the user. Check for an existing
task or project before creating one when duplicates are possible. Examples:

```bash
todoist tasks add "Buy milk" --due "tomorrow"
todoist tasks update TASK_ID --content "Buy oat milk"
todoist tasks close TASK_ID
todoist projects add "Shopping List"
```

The `tasks`, `projects`, `sections`, `labels`, and `comments` groups also expose
other operations through `--help`. Prefer these commands for ordinary work.
Use `sync` when the request needs Todoist Sync API data. Use `raw` only when no
resource command covers the endpoint; it does not validate endpoint-specific
fields. Check the command result, and read back the affected item when needed.
If a request fails, report the failure without claiming the change succeeded.
