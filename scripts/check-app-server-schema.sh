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
if [ ! -d "$schema_dir" ]; then
  echo "Committed app-server schema is missing; run make generate first." >&2
  exit 2
fi

schema_tmp="$(mktemp -d "${TMPDIR:-/tmp}/yijie-codex-schema-check.XXXXXX")"
cleanup() {
  rm -rf -- "$schema_tmp"
}
trap cleanup EXIT

generated_dir="$schema_tmp/generated-json-schema"
"$binary_path" app-server generate-json-schema --out "$generated_dir"
python3 "$repo_root/scripts/canonicalize-json.py" --directory "$generated_dir"

if ! diff -qr "$schema_dir" "$generated_dir"; then
  echo "Committed app-server schema does not match the pinned runtime." >&2
  echo "Run make generate and review the schema changes." >&2
  exit 1
fi

python3 - "$schema_root/baseline.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    metadata = json.load(handle)

required = {
    "schemaVersion": 1,
    "experimentalApi": False,
    "transport": "stdio",
}
for key, expected in required.items():
    if metadata.get(key) != expected:
        raise SystemExit(f"Unexpected schema baseline metadata for {key}: {metadata.get(key)!r}")
PY

echo "Verified committed app-server schema against $binary_path."
