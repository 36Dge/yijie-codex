#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

shopt -s nullglob
patches=(.yijie/patches/*.patch)
shopt -u nullglob

if [ "${#patches[@]}" -ne 0 ]; then
  echo "Runtime Baseline 0 requires an empty Yijie patch set." >&2
  printf 'Unexpected patch: %s\n' "${patches[@]}" >&2
  exit 1
fi

"$repo_root/scripts/verify-upstream-source.sh"
echo "Runtime Baseline 0 patch set is empty."
