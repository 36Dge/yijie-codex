#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$repo_root/scripts/runtime-env.sh"
load_upstream_metadata "$repo_root"
[[ "$(runtime_host_target)" == aarch64-apple-darwin ]]
[[ "$(rustc --version | awk '{print $2}')" == "$YIJIE_CODEX_RUST_TOOLCHAIN" ]]
artifact="$repo_root/.yijie/build/answer-completion-v1/aarch64-apple-darwin"
prepare_script="prepare-answer-completion.py"
manifest_script="write-answer-completion-runtime-manifest.py"
if [[ "$#" == 1 && "$1" == "--execution-progress" ]]; then
  artifact="$repo_root/.yijie/build/execution-progress-v1/aarch64-apple-darwin"
  prepare_script="prepare-execution-progress.py"
  manifest_script="write-execution-progress-runtime-manifest.py"
elif [[ "$#" == 1 && "$1" == "--public-progress-completion" ]]; then
  artifact="$repo_root/.yijie/build/public-progress-completion-v1/aarch64-apple-darwin"
  prepare_script="prepare-public-progress-completion.py"
  manifest_script="write-public-progress-completion-runtime-manifest.py"
elif [[ "$#" == 1 && "$1" == "--native-public-messages" ]]; then
  artifact="$repo_root/.yijie/build/native-public-messages-v1/aarch64-apple-darwin"
  prepare_script="prepare-native-public-messages.py"
  manifest_script="write-native-public-messages-runtime-manifest.py"
elif [[ "$#" != 0 ]]; then
  echo "Unsupported canonical build arguments" >&2
  exit 2
fi
workspace="$repo_root/.local/web-retrieval-guard/workspace"
if [[ -e "$artifact/codex" || -e "$artifact/runtime-manifest.json" ]]; then
  echo "Guard artifact already exists; validate it instead of replacing a published Runtime." >&2
  exit 2
fi
python3 "$repo_root/scripts/$prepare_script"
mkdir -p "$artifact"
python3 "$repo_root/scripts/verify-release-lock-drift.py" \
  --upstream-lock "$repo_root/codex-rs/Cargo.lock" --resolved-lock "$workspace/Cargo.lock" \
  --runtime-version "$YIJIE_CODEX_RUNTIME_VERSION" --report "$artifact/lock-normalization.json"
export CARGO_TARGET_DIR="$repo_root/codex-rs/target"
python3 - "$repo_root" <<'PY'
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1])
names = list((root / ".yijie/patches").rglob("*.patch")) + [root / "scripts" / name for name in (
    "build-answer-completion.sh", "prepare-answer-completion.py", "write-answer-completion-runtime-manifest.py",
    "build-execution-progress.sh", "prepare-execution-progress.py", "write-execution-progress-runtime-manifest.py",
    "build-public-progress-completion.sh", "prepare-public-progress-completion.py", "write-public-progress-completion-runtime-manifest.py",
    "build-native-public-messages.sh", "prepare-native-public-messages.py", "write-native-public-messages-runtime-manifest.py")]
record = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in names}
(root / ".local/web-retrieval-guard/build-inputs.json").write_text(json.dumps(record))
PY
cargo test --offline --locked --manifest-path "$workspace/Cargo.toml" --package codex-core --lib answer_completion_ -- --test-threads=1
if [[ "$prepare_script" == prepare-native-public-messages.py ]]; then
  cargo test --offline --locked --manifest-path "$workspace/Cargo.toml" --package codex-core --lib public_messages_ -- --test-threads=1
fi
cargo clippy --offline --locked --manifest-path "$workspace/Cargo.toml" --package codex-core --lib --no-deps -- -D warnings
cargo build --offline --locked --manifest-path "$workspace/Cargo.toml" --release --package codex-cli --bin codex --target aarch64-apple-darwin
python3 "$repo_root/scripts/$prepare_script" --check
python3 - "$repo_root" <<'PY'
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1])
for name, digest in json.loads((root / ".local/web-retrieval-guard/build-inputs.json").read_text()).items():
    if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
        raise SystemExit("Build inputs changed during compilation; refusing artifact qualification")
PY
install -m 0755 "$CARGO_TARGET_DIR/aarch64-apple-darwin/release/codex" "$artifact/codex"
"$artifact/codex" app-server generate-json-schema --out "$artifact/generated-json-schema"
python3 "$repo_root/scripts/canonicalize-json.py" --directory "$artifact/generated-json-schema"
python3 "$repo_root/scripts/$manifest_script" --profile input-only \
  --binary "$artifact/codex" --schema-dir "$artifact/generated-json-schema" \
  --output "$artifact/runtime-manifest.json" --target aarch64-apple-darwin \
  --upstream-url "$YIJIE_CODEX_UPSTREAM_URL" --upstream-tag "$YIJIE_CODEX_UPSTREAM_TAG" \
  --upstream-commit "$YIJIE_CODEX_UPSTREAM_COMMIT" --runtime-version "$YIJIE_CODEX_RUNTIME_VERSION" \
  --rust-toolchain "$YIJIE_CODEX_RUST_TOOLCHAIN" --patch-dir "$repo_root/.yijie/patches" \
  --lock-normalization "$artifact/lock-normalization.json"
python3 - "$repo_root" "$artifact" <<'PY'
import json
import sys
from pathlib import Path
root, artifact = map(Path, sys.argv[1:])
old = json.loads((root / ".yijie/build/kimi-k31-pro-r5/aarch64-apple-darwin/runtime-manifest.json").read_text())
new = json.loads((artifact / "runtime-manifest.json").read_text())
assert old["appServer"]["schemaTreeSha256"] == new["appServer"]["schemaTreeSha256"]
assert old["appServer"]["schemaFileCount"] == new["appServer"]["schemaFileCount"]
print("Canonical completion Runtime built; app-server schema unchanged; activation not performed.")
PY
