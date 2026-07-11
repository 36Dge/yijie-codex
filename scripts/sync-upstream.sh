#!/usr/bin/env bash
set -euo pipefail

if ! git remote get-url upstream >/dev/null 2>&1; then
  echo "Codex upstream remote is not configured." >&2
  exit 2
fi

git fetch --tags --prune upstream
