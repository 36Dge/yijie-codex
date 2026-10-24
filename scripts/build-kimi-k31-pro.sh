#!/usr/bin/env bash
set -euo pipefail

# FEAT-156: independent candidate output, shared existing Cargo cache.
# Preserve both fixed FEAT-136 and input-only artifacts; no retired patches.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$repo_root/scripts/runtime-env.sh"
load_upstream_metadata "$repo_root"
target="${YIJIE_RUNTIME_TARGET:-$(runtime_host_target)}"
if [[ "$target" != aarch64-apple-darwin ]]; then
  echo "Chat-model stream-arguments candidate is qualified only on aarch64-apple-darwin." >&2
  exit 2
fi
if [[ "$(rustc --version | awk '{print $2}')" != "$YIJIE_CODEX_RUST_TOOLCHAIN" ]]; then
  echo "Pinned Rust toolchain is required." >&2
  exit 2
fi
# FEAT-164 independent canonical output; previous binaries and source scripts stay unchanged.
if [[ "$#" != 0 ]]; then
  echo "Expected no arguments." >&2
  exit 2
fi
candidate=kimi-k31-pro-r1
manifest_writer=write-kimi-k31-pro-runtime-manifest.py
artifact_dir="$repo_root/.yijie/build/$candidate/$target"
schema_dir="$artifact_dir/generated-json-schema"
if [[ -e "$artifact_dir/codex" || -e "$artifact_dir/runtime-manifest.json" ]]; then
  echo "Candidate already exists; refusing to overwrite. Verify it or choose a reviewed new revision." >&2
  exit 2
fi
mkdir -p "$artifact_dir"
build_dir="$(mktemp -d "${TMPDIR:-/tmp}/yijie-chat-model-stream-build.XXXXXX")"
trap 'rm -rf -- "$build_dir"' EXIT
workspace="$build_dir/codex-rs"
mkdir -p "$workspace"
git -C "$repo_root" archive "$YIJIE_CODEX_UPSTREAM_COMMIT:$YIJIE_CODEX_UPSTREAM_SUBTREE" |
  tar -x -C "$workspace"
patches=(
  .yijie/patches/0001-feat-126-filter-persistent-diagnostics.patch
  .yijie/patches/0002-feat-136-unified-exec-pre-emitter-command-lifecycle.patch
  .yijie/patches/input-only/0003-input-only-execution.patch
  .yijie/patches/chat-models/0004-feat-156-upstream-tool-choice.patch
  .yijie/patches/chat-models/0005-feat-156-terminal-tool-arguments.patch
)
if [[ "$candidate" == kimi-k31-pro-r1 ]]; then
  patches+=(.yijie/patches/chat-models/0006-native-web-search-sources.patch .yijie/patches/chat-models/0007-feat-164-kimi-k31-pro.patch)
fi
for patch in "${patches[@]}"; do
  [[ -f "$repo_root/$patch" && ! -L "$repo_root/$patch" ]]
  git -C "$workspace" apply --check "$repo_root/$patch"
  git -C "$workspace" apply "$repo_root/$patch"
done
python3 - "$repo_root" "$build_dir/applied-patches.json" "${patches[@]}" <<'PY'
import hashlib
import json
import sys
from pathlib import Path
root, output = map(Path, sys.argv[1:3])
output.write_text(json.dumps({name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                              for name in sys.argv[3:]}))
PY
cargo metadata --offline --format-version 1 --filter-platform "$target" \
  --manifest-path "$workspace/Cargo.toml" >/dev/null
python3 "$repo_root/scripts/verify-release-lock-drift.py" \
  --upstream-lock "$repo_root/codex-rs/Cargo.lock" \
  --resolved-lock "$workspace/Cargo.lock" \
  --runtime-version "$YIJIE_CODEX_RUNTIME_VERSION" \
  --report "$artifact_dir/lock-normalization.json"
install -m 0644 "$workspace/Cargo.lock" "$artifact_dir/resolved-Cargo.lock"
rustfmt --edition 2024 --check "$workspace/codex-api/src/sse/responses.rs"
CARGO_TARGET_DIR="$repo_root/codex-rs/target" cargo test --offline --locked \
  --manifest-path "$workspace/Cargo.toml" --package codex-api feat156_ -- --test-threads=1
CARGO_TARGET_DIR="$repo_root/codex-rs/target" cargo clippy --offline --locked \
  --manifest-path "$workspace/Cargo.toml" --package codex-api --lib -- -D warnings
if [[ "$candidate" == kimi-k31-pro-r1 ]]; then
  CARGO_TARGET_DIR="$repo_root/codex-rs/target" cargo test --offline --locked \
    --manifest-path "$workspace/Cargo.toml" --package codex-protocol --package codex-app-server-protocol \
    --lib source_web_sources -- --test-threads=1
fi
rustfmt --edition 2024 --check "$workspace/core/src/client.rs" "$workspace/core/src/client_tests.rs"
CARGO_TARGET_DIR="$repo_root/codex-rs/target" cargo test --offline --locked \
  --manifest-path "$workspace/Cargo.toml" --package codex-core --lib feat164_ -- --test-threads=1
CARGO_TARGET_DIR="$repo_root/codex-rs/target" cargo build --offline --locked \
  --manifest-path "$workspace/Cargo.toml" --release \
  --package codex-cli --bin codex --target "$target"
install -m 0755 "$repo_root/codex-rs/target/$target/release/codex" "$artifact_dir/codex"
"$artifact_dir/codex" app-server generate-json-schema --out "$build_dir/schema"
python3 "$repo_root/scripts/canonicalize-json.py" --directory "$build_dir/schema"
mkdir -p "$schema_dir"
# This directory belongs exclusively to this candidate's canonical generator.
python3 - "$build_dir/schema" "$schema_dir" <<'PY'
import shutil
import sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
for path in target.rglob("*.json"):
    if not (source / path.relative_to(target)).exists():
        path.unlink()
shutil.copytree(source, target, dirs_exist_ok=True)
PY
python3 - "$repo_root" "$build_dir/applied-patches.json" <<'PY'
import hashlib
import json
import sys
from pathlib import Path
root, record = map(Path, sys.argv[1:])
for name, digest in json.loads(record.read_text()).items():
    if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
        raise SystemExit("Source changed during build; refusing a mismatched manifest")
PY
python3 "$repo_root/scripts/$manifest_writer" \
  --profile input-only --binary "$artifact_dir/codex" --schema-dir "$schema_dir" \
  --output "$artifact_dir/runtime-manifest.json" --target "$target" \
  --upstream-url "$YIJIE_CODEX_UPSTREAM_URL" --upstream-tag "$YIJIE_CODEX_UPSTREAM_TAG" \
  --upstream-commit "$YIJIE_CODEX_UPSTREAM_COMMIT" --runtime-version "$YIJIE_CODEX_RUNTIME_VERSION" \
  --rust-toolchain "$YIJIE_CODEX_RUST_TOOLCHAIN" --patch-dir "$repo_root/.yijie/patches" \
  --lock-normalization "$artifact_dir/lock-normalization.json"
if [[ "$candidate" == kimi-k31-pro-r1 ]]; then
  python3 "$repo_root/scripts/verify-web-search-sources-schema.py" "$schema_dir"
  diff -qr "$schema_dir" "$repo_root/.yijie/build/chat-models-web-sources/$target/generated-json-schema"
  python3 "$repo_root/scripts/app-server-smoke.py" --binary "$artifact_dir/codex" --expected-version "$YIJIE_CODEX_RUNTIME_VERSION"
else
python3 - "$repo_root" "$schema_dir" <<'PYSCHEMA'
import sys
from pathlib import Path
root, generated = map(Path, sys.argv[1:])
fixed = root / ".yijie/schemas/input-only-app-server/generated-json-schema"
a = {p.relative_to(fixed).as_posix(): p.read_bytes() for p in fixed.rglob("*.json")}
b = {p.relative_to(generated).as_posix(): p.read_bytes() for p in generated.rglob("*.json")}
if a != b or len(b) != 269:
    raise SystemExit("FEAT-156 canonical schema differs from fixed input-only authority")
print("269 stable schemas equal the fixed input-only source")
PYSCHEMA
fi
echo "FEAT-164 Kimi K3.1 Pro candidate built with shared codex-rs/target cache: $artifact_dir"
