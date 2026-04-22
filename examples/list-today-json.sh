#!/usr/bin/env bash
set -euo pipefail

: "${TODOIST_API_TOKEN:?Set TODOIST_API_TOKEN before running this script.}"

todoist --format json tasks list --filter-query "today"
