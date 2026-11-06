#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$root/scripts/runtime-env.sh"
load_upstream_metadata "$root"
target="$(runtime_host_target)"
[[ "$target" == "$YIJIE_CODEX_PRIMARY_RELEASE_TARGET" ]]
[[ "$(rustc --version | awk '{print $2}')" == "$YIJIE_CODEX_RUST_TOOLCHAIN" ]]
artifact="$root/.yijie/build/host-images-v1/$target"
work="$root/.local/host-images/workspace"
[[ ! -e "$artifact" ]] || { echo 'Image candidate already exists; refusing to replace it.' >&2; exit 2; }
python3 "$root/scripts/prepare-host-images.py"
# Cargo intermediates are reproducible build outputs. Final candidate directories are immutable.
export CARGO_TARGET_DIR="$root/codex-rs/target"
cargo build --offline --locked --manifest-path "$work/Cargo.toml" --package codex-cli --bin codex --release --target "$target"
python3 "$root/scripts/prepare-host-images.py" --check
staging="$(mktemp -d "$root/.local/host-images/artifact.XXXXXX")"
python3 "$root/scripts/verify-release-lock-drift.py" --upstream-lock "$root/codex-rs/Cargo.lock" --resolved-lock "$work/Cargo.lock" --runtime-version "$YIJIE_CODEX_RUNTIME_VERSION" --report "$staging/lock-normalization.json"
install -m 0755 "$CARGO_TARGET_DIR/$target/release/codex" "$staging/codex"
"$staging/codex" app-server generate-json-schema --out "$staging/generated-json-schema"
python3 "$root/scripts/canonicalize-json.py" --directory "$staging/generated-json-schema"
python3 "$root/scripts/write-host-image-runtime-manifest.py" --profile input-only --binary "$staging/codex" --schema-dir "$staging/generated-json-schema" --output "$staging/runtime-manifest.json" --target "$target" --upstream-url "$YIJIE_CODEX_UPSTREAM_URL" --upstream-tag "$YIJIE_CODEX_UPSTREAM_TAG" --upstream-commit "$YIJIE_CODEX_UPSTREAM_COMMIT" --runtime-version "$YIJIE_CODEX_RUNTIME_VERSION" --rust-toolchain "$YIJIE_CODEX_RUST_TOOLCHAIN" --patch-dir "$root/.yijie/patches" --lock-normalization "$staging/lock-normalization.json"
test -s "$staging/generated-json-schema/HostImageGenerateParams.json"
test -s "$staging/generated-json-schema/HostImageGenerateResponse.json"
mkdir -p "$(dirname "$artifact")"
mv "$staging" "$artifact"
printf 'Built isolated Host image candidate: %s\n' "$artifact"
