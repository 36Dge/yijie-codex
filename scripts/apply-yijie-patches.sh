#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if [ "$#" -gt 1 ]; then
  echo "Usage: $0 [temporary-codex-rs-workspace]" >&2
  exit 2
fi

expected_patch=".yijie/patches/0001-feat-126-filter-persistent-diagnostics.patch"
shopt -s nullglob
patches=(.yijie/patches/*.patch)
shopt -u nullglob
if [ "${#patches[@]}" -ne 1 ] || [ "${patches[0]}" != "$expected_patch" ]; then
  echo "Runtime patch set does not match the reviewed FEAT-126 overlay." >&2
  exit 1
fi
for patch in "${patches[@]}"; do
  if [ ! -f "$patch" ] || [ -L "$patch" ]; then
    echo "Missing or unsafe Yijie Runtime patch: $patch" >&2
    exit 1
  fi
done

workspace="${1:-}"
validation_dir=""
if [ -z "$workspace" ]; then
  "$repo_root/scripts/verify-upstream-source.sh"
  # shellcheck source=runtime-env.sh
  source "$repo_root/scripts/runtime-env.sh"
  load_upstream_metadata "$repo_root"
  validation_dir="$(mktemp -d "${TMPDIR:-/tmp}/yijie-codex-patch-check.XXXXXX")"
  trap 'rm -rf -- "$validation_dir"' EXIT
  workspace="$validation_dir/codex-rs"
  mkdir -p "$workspace"
  git archive "$YIJIE_CODEX_UPSTREAM_COMMIT:$YIJIE_CODEX_UPSTREAM_SUBTREE" \
    | tar -x -C "$workspace"
fi

if [ ! -f "$workspace/Cargo.toml" ]; then
  echo "Patch workspace does not contain codex-rs/Cargo.toml: $workspace" >&2
  exit 2
fi
if [ "$(cd "$workspace" && pwd -P)" = "$(cd "$repo_root/codex-rs" && pwd -P)" ]; then
  echo "Refusing to apply Yijie patches to canonical codex-rs materialization." >&2
  exit 2
fi

for patch in "${patches[@]}"; do
  patch_path="$repo_root/$patch"
  (cd "$workspace" && git apply --check "$patch_path")
  (cd "$workspace" && git apply "$patch_path")
done

echo "Applied ${#patches[@]} Yijie Runtime patch(es) to temporary workspace."
