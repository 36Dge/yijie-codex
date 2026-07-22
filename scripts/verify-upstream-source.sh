#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# shellcheck source=runtime-env.sh
source "$repo_root/scripts/runtime-env.sh"
load_upstream_metadata "$repo_root"

if [ ! -f codex-rs/Cargo.toml ]; then
  echo "Codex source is not materialized." >&2
  exit 2
fi
if ! git cat-file -e "$YIJIE_CODEX_UPSTREAM_COMMIT^{commit}" 2>/dev/null; then
  echo "Pinned upstream commit is not available locally; run make sync first." >&2
  exit 2
fi

verify_dir="$(mktemp -d "${TMPDIR:-/tmp}/yijie-codex-verify.XXXXXX")"
cleanup() {
  rm -rf -- "$verify_dir"
}
trap cleanup EXIT

mkdir -p "$verify_dir/codex-rs" "$verify_dir/root"
git archive "$YIJIE_CODEX_UPSTREAM_COMMIT:$YIJIE_CODEX_UPSTREAM_SUBTREE" \
  | tar -x -C "$verify_dir/codex-rs"
git archive "$YIJIE_CODEX_UPSTREAM_COMMIT" LICENSE NOTICE \
  | tar -x -C "$verify_dir/root"

if ! runtime_source_diff codex-rs "$verify_dir/codex-rs"; then
  echo "codex-rs differs from the pinned zero-patch upstream source." >&2
  exit 1
fi
if ! cmp -s LICENSE "$verify_dir/root/LICENSE"; then
  echo "LICENSE differs from the pinned upstream source." >&2
  exit 1
fi
if ! cmp -s NOTICE "$verify_dir/root/NOTICE"; then
  echo "NOTICE differs from the pinned upstream source." >&2
  exit 1
fi

echo "Verified zero-patch source against $YIJIE_CODEX_UPSTREAM_TAG ($YIJIE_CODEX_UPSTREAM_COMMIT)."
