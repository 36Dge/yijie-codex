#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$repo_root/scripts/runtime-env.sh"
load_upstream_metadata "$repo_root"
artifact="$repo_root/.yijie/build/chat-models-stream-args/aarch64-apple-darwin"
verification_dir="$(mktemp -d "${TMPDIR:-/tmp}/yijie-chat-model-check.XXXXXX")"
trap 'rm -rf -- "$verification_dir"' EXIT
mkdir -p "$verification_dir/source"
git -C "$repo_root" archive "$YIJIE_CODEX_UPSTREAM_COMMIT:$YIJIE_CODEX_UPSTREAM_SUBTREE" |
  tar -x -C "$verification_dir/source"
for patch in \
  .yijie/patches/0001-feat-126-filter-persistent-diagnostics.patch \
  .yijie/patches/0002-feat-136-unified-exec-pre-emitter-command-lifecycle.patch \
  .yijie/patches/input-only/0003-input-only-execution.patch; do
  git -C "$verification_dir/source" apply "$repo_root/$patch"
done
cp "$verification_dir/source/core/src/client.rs" "$verification_dir/input-only-client.rs"
patch="$repo_root/.yijie/patches/chat-models/0004-feat-156-upstream-tool-choice.patch"
git -C "$verification_dir/source" apply --check "$patch"
git -C "$verification_dir/source" apply "$patch"
git -C "$repo_root" show "$YIJIE_CODEX_UPSTREAM_COMMIT:$YIJIE_CODEX_UPSTREAM_SUBTREE/core/src/client.rs" > "$verification_dir/upstream-client.rs"
cmp "$verification_dir/upstream-client.rs" "$verification_dir/source/core/src/client.rs"
git -C "$verification_dir/source" apply --reverse "$patch"
cmp "$verification_dir/input-only-client.rs" "$verification_dir/source/core/src/client.rs"
stream_patch="$repo_root/.yijie/patches/chat-models/0005-feat-156-terminal-tool-arguments.patch"
cp "$verification_dir/source/codex-api/src/sse/responses.rs" "$verification_dir/original-responses.rs"
git -C "$verification_dir/source" apply --check "$stream_patch"
git -C "$verification_dir/source" apply "$stream_patch"
git -C "$verification_dir/source" apply --reverse "$stream_patch"
cmp "$verification_dir/source/codex-api/src/sse/responses.rs" "$verification_dir/original-responses.rs"
git -C "$verification_dir/source" apply "$patch"
git -C "$verification_dir/source" apply "$stream_patch"
cargo metadata --offline --format-version 1 --manifest-path "$verification_dir/source/Cargo.toml" >/dev/null
python3 "$repo_root/scripts/verify-release-lock-drift.py" \
  --upstream-lock "$repo_root/codex-rs/Cargo.lock" \
  --resolved-lock "$verification_dir/source/Cargo.lock" \
  --runtime-version "$YIJIE_CODEX_RUNTIME_VERSION" \
  --report "$verification_dir/lock-normalization.json"
CARGO_TARGET_DIR="$repo_root/codex-rs/target" cargo test --offline --locked \
  --manifest-path "$verification_dir/source/Cargo.toml" --package codex-api --lib sse::responses::tests
"$artifact/codex" app-server generate-json-schema --out "$verification_dir/schema"
python3 "$repo_root/scripts/canonicalize-json.py" --directory "$verification_dir/schema"
diff -qr "$verification_dir/schema" "$artifact/generated-json-schema"
diff -qr "$verification_dir/schema" "$repo_root/.yijie/schemas/input-only-app-server/generated-json-schema"
python3 "$repo_root/scripts/app-server-smoke.py" --binary "$artifact/codex" --expected-version "$YIJIE_CODEX_RUNTIME_VERSION"
if [[ -d "$repo_root/../yijie-contracts" ]]; then
  node "$repo_root/../yijie-contracts/scripts/generate-runtime-chat-models.mjs" --check
  node "$repo_root/../yijie-contracts/scripts/sync-runtime-chat-models.mjs" --check
else
  echo "SKIP: Contracts sibling unavailable; cross-repository validation incomplete."
fi
echo "FEAT-156 replay/reverse, upstream client equality, stable schema and normal-EOF handshake passed."
