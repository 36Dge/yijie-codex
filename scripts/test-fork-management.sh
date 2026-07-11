#!/usr/bin/env bash
set -euo pipefail

required=(README.md UPSTREAM.md CHANGELOG.yijie.md docs/upstream-sync.md docs/yijie-patch-policy.md)
for file in "${required[@]}"; do
  if [ ! -s "$file" ]; then
    echo "Missing or empty fork-management file: $file" >&2
    exit 1
  fi
done

bash -n scripts/*.sh
for script in scripts/*.sh; do
  if [ ! -x "$script" ]; then
    echo "Script is not executable: $script" >&2
    exit 1
  fi
done

echo "Fork-management metadata and scripts are valid."
