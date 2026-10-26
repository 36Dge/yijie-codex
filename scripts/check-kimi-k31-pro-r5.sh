#!/usr/bin/env bash
set -euo pipefail

# Ordinary source replay and focused lint; no provider or process-failure tests.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$repo_root/scripts/runtime-env.sh"
load_upstream_metadata "$repo_root"
[[ "$#" == 0 && "$(rustc --version | awk '{print $2}')" == "$YIJIE_CODEX_RUST_TOOLCHAIN" ]]
check_dir="$(mktemp -d "${TMPDIR:-/tmp}/yijie-kimi-r5-check.XXXXXX")"
trap 'rm -rf -- "$check_dir"' EXIT
workspace="$check_dir/codex-rs"
mkdir -p "$workspace"
git -C "$repo_root" archive "$YIJIE_CODEX_UPSTREAM_COMMIT:$YIJIE_CODEX_UPSTREAM_SUBTREE" | tar -x -C "$workspace"
patches=(
  .yijie/patches/0001-feat-126-filter-persistent-diagnostics.patch
  .yijie/patches/0002-feat-136-unified-exec-pre-emitter-command-lifecycle.patch
  .yijie/patches/input-only/0003-input-only-execution.patch
  .yijie/patches/chat-models/0004-feat-156-upstream-tool-choice.patch
  .yijie/patches/chat-models/0005-feat-156-terminal-tool-arguments.patch
  .yijie/patches/chat-models/0006-native-web-search-sources.patch
  .yijie/patches/chat-models/0007-feat-164-kimi-k31-pro.patch
  .yijie/patches/chat-models/0008-feat-164-kimi-responses-include.patch
  .yijie/patches/chat-models/0009-feat-164-native-failure-terminals.patch
  .yijie/patches/chat-models/0010-feat-164-sanitized-persistence-metrics.patch
  .yijie/patches/chat-models/0011-feat-164-graceful-state-close.patch
)
for patch in "${patches[@]}"; do
  [[ -f "$repo_root/$patch" && ! -L "$repo_root/$patch" ]]
  git -C "$workspace" apply --check "$repo_root/$patch"
  git -C "$workspace" apply "$repo_root/$patch"
done
cargo metadata --offline --format-version 1 --filter-platform "$(runtime_host_target)" --manifest-path "$workspace/Cargo.toml" >/dev/null
python3 "$repo_root/scripts/verify-release-lock-drift.py" --upstream-lock "$repo_root/codex-rs/Cargo.lock" \
  --resolved-lock "$workspace/Cargo.lock" --runtime-version "$YIJIE_CODEX_RUNTIME_VERSION" --report "$check_dir/lock-normalization.json"
rustfmt --edition 2024 --config skip_children=true --check "$workspace/app-server/src/lib.rs" "$workspace/app-server/src/message_processor.rs" "$workspace/app-server/src/request_processors/thread_processor.rs" "$workspace/state/src/log_db.rs" "$workspace/app-server/src/thread_state.rs" "$workspace/app-server/src/request_processors/thread_lifecycle.rs"
CARGO_TARGET_DIR="$repo_root/codex-rs/target" cargo test --offline --locked --manifest-path "$workspace/Cargo.toml" \
  --package codex-state --package codex-app-server --lib feat164_ -- --test-threads=1
CARGO_TARGET_DIR="$repo_root/codex-rs/target" cargo test --offline --locked --manifest-path "$workspace/Cargo.toml" \
  --package codex-app-server --lib connection_rpc_gate::tests -- --test-threads=1
CARGO_TARGET_DIR="$repo_root/codex-rs/target" cargo clippy --offline --locked --manifest-path "$workspace/Cargo.toml" \
  --package codex-state --package codex-app-server --lib --no-deps -- -D warnings
