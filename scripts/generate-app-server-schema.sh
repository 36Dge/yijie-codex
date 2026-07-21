#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# shellcheck source=runtime-env.sh
source "$repo_root/scripts/runtime-env.sh"
load_upstream_metadata "$repo_root"

target="${YIJIE_RUNTIME_TARGET:-$(runtime_host_target)}"
binary_path="$(runtime_binary_path "$repo_root" "$target")"
schema_root="$repo_root/.yijie/schemas/app-server"
schema_dir="$schema_root/generated-json-schema"

if [ ! -x "$binary_path" ]; then
  echo "Runtime binary is missing; run make build first: $binary_path" >&2
  exit 2
fi

schema_tmp="$(mktemp -d "${TMPDIR:-/tmp}/yijie-codex-schema.XXXXXX")"
cleanup() {
  rm -rf -- "$schema_tmp"
}
trap cleanup EXIT

generated_dir="$schema_tmp/generated-json-schema"
"$binary_path" app-server generate-json-schema --out "$generated_dir"
python3 "$repo_root/scripts/canonicalize-json.py" --directory "$generated_dir"

if [ -z "$(find "$generated_dir" -type f -name '*.json' -print -quit)" ]; then
  echo "App-server schema generation produced no JSON files." >&2
  exit 1
fi

mkdir -p "$schema_root"
previous_schema="$schema_tmp/previous-generated-json-schema"
if [ -d "$schema_dir" ]; then
  mv "$schema_dir" "$previous_schema"
fi
mv "$generated_dir" "$schema_dir"

cat > "$schema_root/baseline.json.tmp" <<EOF
{
  "schemaVersion": 1,
  "upstreamTag": "$YIJIE_CODEX_UPSTREAM_TAG",
  "upstreamCommit": "$YIJIE_CODEX_UPSTREAM_COMMIT",
  "runtimeVersion": "$YIJIE_CODEX_RUNTIME_VERSION",
  "rustToolchain": "$YIJIE_CODEX_RUST_TOOLCHAIN",
  "primaryReleaseTarget": "$YIJIE_CODEX_PRIMARY_RELEASE_TARGET",
  "experimentalApi": false,
  "transport": "stdio"
}
EOF
mv "$schema_root/baseline.json.tmp" "$schema_root/baseline.json"

schema_count="$(find "$schema_dir" -type f -name '*.json' | wc -l | tr -d ' ')"
echo "Generated $schema_count stable app-server JSON Schema files from $binary_path."
