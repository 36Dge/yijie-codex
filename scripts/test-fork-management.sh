#!/usr/bin/env bash
set -euo pipefail

required=(
  README.md
  UPSTREAM.md
  CHANGELOG.yijie.md
  LICENSE
  NOTICE
  .yijie/upstream.env
  .yijie/schemas/app-server/baseline.json
  .yijie/schemas/app-server/generated-json-schema/codex_app_server_protocol.schemas.json
  codex-rs/Cargo.toml
  codex-rs/Cargo.lock
  docs/upstream-sync.md
  docs/yijie-patch-policy.md
  docs/runtime-compatibility.md
  docs/runtime-baseline-0.md
  scripts/check_agent_host_contracts.py
  scripts/app-server-smoke.py
  scripts/runtime_manifest.py
  scripts/test_app_server_smoke.py
  scripts/test_agent_host_contracts.py
  scripts/test_write_runtime_manifest.py
  scripts/write-runtime-manifest.py
)
for file in "${required[@]}"; do
  if [ ! -s "$file" ]; then
    echo "Missing or empty fork-management file: $file" >&2
    exit 1
  fi
done

bash -n scripts/*.sh
./scripts/lint-python.sh
for script in scripts/*.sh; do
  if [ ! -x "$script" ]; then
    echo "Script is not executable: $script" >&2
    exit 1
  fi
done
for script in scripts/*.py; do
  if [ ! -x "$script" ]; then
    echo "Script is not executable: $script" >&2
    exit 1
  fi
done

# shellcheck source=runtime-env.sh
source scripts/runtime-env.sh
load_upstream_metadata "$(pwd)"
if [ "$YIJIE_CODEX_UPSTREAM_TAG" != "rust-v$YIJIE_CODEX_RUNTIME_VERSION" ]; then
  echo "Pinned tag and runtime version disagree." >&2
  exit 1
fi
if [ "$YIJIE_CODEX_PRIMARY_RELEASE_TARGET" != "aarch64-apple-darwin" ]; then
  echo "Runtime Baseline 0 must retain the macOS Apple Silicon release target." >&2
  exit 1
fi
if [ "$YIJIE_CODEX_RUST_TOOLCHAIN" != "1.95.0" ]; then
  echo "Runtime Baseline 0 must retain Rust 1.95.0." >&2
  exit 1
fi

source_diff_test_dir="$(mktemp -d "${TMPDIR:-/tmp}/yijie-source-diff-test.XXXXXX")"
cleanup_source_diff_test() {
  rm -rf -- "$source_diff_test_dir"
}
trap cleanup_source_diff_test EXIT
mkdir -p "$source_diff_test_dir/actual/target" "$source_diff_test_dir/expected"
printf 'same\n' >"$source_diff_test_dir/actual/source.txt"
printf 'same\n' >"$source_diff_test_dir/expected/source.txt"
printf 'finder metadata\n' >"$source_diff_test_dir/actual/.DS_Store"
printf 'build output\n' >"$source_diff_test_dir/actual/target/local.txt"
if ! runtime_source_diff "$source_diff_test_dir/actual" "$source_diff_test_dir/expected" >/dev/null; then
  echo "Runtime source comparison must ignore local Finder and Cargo artifacts." >&2
  exit 1
fi
printf 'changed\n' >"$source_diff_test_dir/actual/source.txt"
if runtime_source_diff "$source_diff_test_dir/actual" "$source_diff_test_dir/expected" >/dev/null; then
  echo "Runtime source comparison failed to detect a real source difference." >&2
  exit 1
fi

python3 - .yijie/schemas/app-server/baseline.json <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    baseline = json.load(handle)

expected = {
    "upstreamTag": "rust-v0.144.6",
    "upstreamCommit": "5d1fbf26c43abc65a203928b2e31561cb039e06d",
    "runtimeVersion": "0.144.6",
    "rustToolchain": "1.95.0",
    "primaryReleaseTarget": "aarch64-apple-darwin",
    "experimentalApi": False,
    "transport": "stdio",
}
for key, value in expected.items():
    if baseline.get(key) != value:
        raise SystemExit(f"Unexpected app-server baseline metadata for {key}")
PY

python3 scripts/test_agent_host_contracts.py
python3 scripts/test_app_server_smoke.py
python3 scripts/test_write_runtime_manifest.py

expected_patches=(
  ".yijie/patches/0001-feat-126-filter-persistent-diagnostics.patch"
  ".yijie/patches/0002-feat-136-unified-exec-pre-emitter-command-lifecycle.patch"
  ".yijie/patches/0003-feat-137-stable-sandbox-provenance.patch"
)
shopt -s nullglob dotglob
patches=(.yijie/patches/*.patch)
shopt -u dotglob nullglob
if [ "${#patches[@]}" -ne "${#expected_patches[@]}" ]; then
  echo "Runtime patch set does not match the reviewed FEAT-126/FEAT-136/FEAT-137 overlays." >&2
  exit 1
fi
for index in "${!expected_patches[@]}"; do
  if [ "${patches[$index]}" != "${expected_patches[$index]}" ]; then
    echo "Runtime patch set order does not match the reviewed FEAT-126/FEAT-136/FEAT-137 overlays." >&2
    exit 1
  fi
done
./scripts/apply-yijie-patches.sh

echo "Fork-management metadata and scripts are valid."
