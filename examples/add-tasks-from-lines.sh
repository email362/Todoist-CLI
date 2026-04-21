#!/usr/bin/env bash
set -euo pipefail

: "${TODOIST_API_TOKEN:?Set TODOIST_API_TOKEN before running this script.}"

if [[ $# -ne 1 ]]; then
  printf 'usage: %s TASK_FILE\n' "$0" >&2
  exit 2
fi

task_file=$1

while IFS= read -r task || [[ -n "$task" ]]; do
  [[ -z "$task" || "$task" == \#* ]] && continue
  todoist tasks add "$task"
done < "$task_file"
