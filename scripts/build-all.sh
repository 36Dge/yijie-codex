#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# shellcheck source=runtime-env.sh
source "$repo_root/scripts/runtime-env.sh"
load_upstream_metadata "$repo_root"

"$repo_root/scripts/apply-yijie-patches.sh"

target="${YIJIE_RUNTIME_TARGET:-$(runtime_host_target)}"
if [ -z "$target" ]; then
  echo "Unable to determine the Rust host target." >&2
  exit 2
fi

actual_rust_version="$(rustc --version | awk '{print $2}')"
if [ "$actual_rust_version" != "$YIJIE_CODEX_RUST_TOOLCHAIN" ]; then
  echo "Rust toolchain mismatch." >&2
  echo "Expected: $YIJIE_CODEX_RUST_TOOLCHAIN" >&2
  echo "Actual:   $actual_rust_version" >&2
  exit 2
fi

artifact_dir="$(runtime_artifact_dir "$repo_root" "$target")"
binary_path="$(runtime_binary_path "$repo_root" "$target")"
mkdir -p "$artifact_dir"

build_dir="$(mktemp -d "${TMPDIR:-/tmp}/yijie-codex-build.XXXXXX")"
cleanup() {
  rm -rf -- "$build_dir"
}
trap cleanup EXIT

build_workspace="$build_dir/codex-rs"
mkdir -p "$build_workspace"
git archive "$YIJIE_CODEX_UPSTREAM_COMMIT:$YIJIE_CODEX_UPSTREAM_SUBTREE" \
  | tar -x -C "$build_workspace"

# The release tag updates workspace.package.version but its checked-in lockfile
# retains 0.0.0 for local packages. Resolve in the disposable workspace, then
# prove that Cargo changed only those local package version fields.
cargo metadata \
  --format-version 1 \
  --filter-platform "$target" \
  --manifest-path "$build_workspace/Cargo.toml" \
  >/dev/null
python3 "$repo_root/scripts/verify-release-lock-drift.py" \
  --upstream-lock "$repo_root/codex-rs/Cargo.lock" \
  --resolved-lock "$build_workspace/Cargo.lock" \
  --runtime-version "$YIJIE_CODEX_RUNTIME_VERSION" \
  --report "$artifact_dir/lock-normalization.json"
install -m 0644 "$build_workspace/Cargo.lock" "$artifact_dir/resolved-Cargo.lock"

CARGO_TARGET_DIR="$repo_root/codex-rs/target" cargo build \
  --locked \
  --manifest-path "$build_workspace/Cargo.toml" \
  --release \
  --package codex-cli \
  --bin codex \
  --target "$target"

source_binary="codex-rs/target/$target/release/codex"
case "$target" in
  *-windows-*|*-pc-windows-*) source_binary="${source_binary}.exe" ;;
esac
if [ ! -x "$source_binary" ]; then
  echo "Expected runtime binary was not produced: $source_binary" >&2
  exit 1
fi

install -m 0755 "$source_binary" "$binary_path"

actual_version="$($binary_path --version)"
case "$actual_version" in
  *"$YIJIE_CODEX_RUNTIME_VERSION"*) ;;
  *)
    echo "Built runtime version does not match the pinned baseline: $actual_version" >&2
    exit 1
    ;;
esac

echo "Built $actual_version for $target at $binary_path"
