#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$root/scripts/runtime-env.sh"
load_upstream_metadata "$root"
target="$(runtime_host_target)"
[[ "$target" == "$YIJIE_CODEX_PRIMARY_RELEASE_TARGET" ]]
[[ "$(rustc --version | awk '{print $2}')" == "$YIJIE_CODEX_RUST_TOOLCHAIN" ]]
output_root="$root/.yijie/build/native-tools-v1"
source_id="$(python3 - "$root" <<'PY'
import hashlib, pathlib, sys
root = pathlib.Path(sys.argv[1])
files = [root / '.yijie/patches/chat-models/0020-native-tool-integration.patch', root / '.yijie/patches/chat-models/0021-native-tool-policy-audit.patch', *[root / 'scripts' / n for n in ['build-native-tools.sh', 'prepare-native-tools.py', 'write-native-tools-runtime-manifest.py']]]
h = hashlib.sha256()
for file in files:
    h.update(file.relative_to(root).as_posix().encode()); h.update(b'\0'); h.update(file.read_bytes())
print(h.hexdigest())
PY
)"
artifact="$output_root/$source_id/$target"
work="$root/.local/native-tools/workspace"
[[ ! -e "$artifact" ]] || { echo 'Native tools candidate exists; refusing to replace it.' >&2; exit 2; }
python3 "$root/scripts/prepare-native-tools.py"
export CARGO_TARGET_DIR="$root/codex-rs/target"
cargo build --offline --locked --manifest-path "$work/Cargo.toml" --package codex-cli --bin codex --release --target "$target"
python3 "$root/scripts/prepare-native-tools.py" --check
staging="$(mktemp -d "$root/.local/native-tools/artifact.XXXXXX")"
python3 "$root/scripts/verify-release-lock-drift.py" --upstream-lock "$root/codex-rs/Cargo.lock" --resolved-lock "$work/Cargo.lock" --runtime-version "$YIJIE_CODEX_RUNTIME_VERSION" --report "$staging/lock-normalization.json"
install -m 0755 "$CARGO_TARGET_DIR/$target/release/codex" "$staging/codex"
"$staging/codex" app-server generate-json-schema --out "$staging/generated-json-schema"
python3 "$root/scripts/canonicalize-json.py" --directory "$staging/generated-json-schema"
# The native config schema is generated from the same patched source, not copied
# from the unpatched upstream snapshot.
cargo run --offline --locked --manifest-path "$work/Cargo.toml" --package codex-core --bin codex-write-config-schema -- --out "$staging/config.schema.json"
python3 "$root/scripts/write-native-tools-runtime-manifest.py" --profile input-only --binary "$staging/codex" --schema-dir "$staging/generated-json-schema" --output "$staging/runtime-manifest.json" --target "$target" --upstream-url "$YIJIE_CODEX_UPSTREAM_URL" --upstream-tag "$YIJIE_CODEX_UPSTREAM_TAG" --upstream-commit "$YIJIE_CODEX_UPSTREAM_COMMIT" --runtime-version "$YIJIE_CODEX_RUNTIME_VERSION" --rust-toolchain "$YIJIE_CODEX_RUST_TOOLCHAIN" --patch-dir "$root/.yijie/patches" --lock-normalization "$staging/lock-normalization.json"
mkdir -p "$(dirname "$artifact")"
mv "$staging" "$artifact"
python3 - "$output_root" "$source_id" "$target" <<'PY'
import json, os, pathlib, sys
root = pathlib.Path(sys.argv[1])
temporary = root / 'current.json.pending'
with temporary.open('x') as f:
    json.dump({'schema_version': 1, 'source_sha256': sys.argv[2], 'artifact': sys.argv[2] + '/' + sys.argv[3]}, f, indent=2)
    f.write('\n')
os.replace(temporary, root / 'current.json')
PY
printf 'Built native tools candidate: %s\n' "$artifact"
