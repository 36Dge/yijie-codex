#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# shellcheck source=runtime-env.sh
source "$repo_root/scripts/runtime-env.sh"
load_upstream_metadata "$repo_root"

"$repo_root/scripts/apply-yijie-patches.sh"

target="${YIJIE_RUNTIME_TARGET:-$(runtime_host_target)}"
binary_path="$(runtime_binary_path "$repo_root" "$target")"
artifact_dir="$(runtime_artifact_dir "$repo_root" "$target")"
schema_dir="$repo_root/.yijie/schemas/app-server/generated-json-schema"
manifest_path="$artifact_dir/runtime-manifest.json"

if [ ! -x "$binary_path" ]; then
  echo "Runtime binary is missing; run make build first: $binary_path" >&2
  exit 2
fi

"$repo_root/scripts/check-app-server-schema.sh"
python3 "$repo_root/scripts/app-server-smoke.py" \
  --binary "$binary_path" \
  --expected-version "$YIJIE_CODEX_RUNTIME_VERSION"
python3 "$repo_root/scripts/write-runtime-manifest.py" \
  --binary "$binary_path" \
  --schema-dir "$schema_dir" \
  --output "$manifest_path" \
  --target "$target" \
  --upstream-url "$YIJIE_CODEX_UPSTREAM_URL" \
  --upstream-tag "$YIJIE_CODEX_UPSTREAM_TAG" \
  --upstream-commit "$YIJIE_CODEX_UPSTREAM_COMMIT" \
  --runtime-version "$YIJIE_CODEX_RUNTIME_VERSION" \
  --rust-toolchain "$YIJIE_CODEX_RUST_TOOLCHAIN" \
  --patch-dir "$repo_root/.yijie/patches" \
  --lock-normalization "$artifact_dir/lock-normalization.json"
python3 "$repo_root/scripts/check_agent_host_contracts.py" \
  --repo-root "$repo_root" \
  --contracts-repo "${YIJIE_CONTRACTS_REPO:-$repo_root/../yijie-contracts}" \
  --runtime-manifest "$manifest_path"

echo "Runtime Baseline 0 compatibility checks passed for $target."
