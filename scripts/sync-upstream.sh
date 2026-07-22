#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

# shellcheck source=runtime-env.sh
source "$repo_root/scripts/runtime-env.sh"
load_upstream_metadata "$repo_root"

if git remote get-url upstream >/dev/null 2>&1; then
  actual_url="$(git remote get-url upstream)"
  if [ "$actual_url" != "$YIJIE_CODEX_UPSTREAM_URL" ]; then
    echo "Unexpected upstream remote: $actual_url" >&2
    echo "Expected: $YIJIE_CODEX_UPSTREAM_URL" >&2
    exit 2
  fi
else
  git remote add upstream "$YIJIE_CODEX_UPSTREAM_URL"
fi
if [ "$(git remote get-url --push upstream)" != "DISABLED" ]; then
  git remote set-url --push upstream DISABLED
fi

git fetch --no-tags upstream \
  "refs/tags/$YIJIE_CODEX_UPSTREAM_TAG:refs/tags/$YIJIE_CODEX_UPSTREAM_TAG"

resolved_commit="$(git rev-parse "$YIJIE_CODEX_UPSTREAM_TAG^{}")"
if [ "$resolved_commit" != "$YIJIE_CODEX_UPSTREAM_COMMIT" ]; then
  echo "Pinned tag resolved to an unexpected commit." >&2
  echo "Expected: $YIJIE_CODEX_UPSTREAM_COMMIT" >&2
  echo "Actual:   $resolved_commit" >&2
  exit 2
fi

sync_dir="$(mktemp -d "${TMPDIR:-/tmp}/yijie-codex-sync.XXXXXX")"
cleanup() {
  rm -rf -- "$sync_dir"
}
trap cleanup EXIT

mkdir -p "$sync_dir/codex-rs" "$sync_dir/root"
git archive "$YIJIE_CODEX_UPSTREAM_COMMIT:$YIJIE_CODEX_UPSTREAM_SUBTREE" \
  | tar -x -C "$sync_dir/codex-rs"
git archive "$YIJIE_CODEX_UPSTREAM_COMMIT" LICENSE NOTICE \
  | tar -x -C "$sync_dir/root"

if [ ! -f "$sync_dir/codex-rs/Cargo.toml" ]; then
  echo "Materialized source does not contain codex-rs/Cargo.toml." >&2
  exit 2
fi

if [ -d codex-rs ] \
  && [ -f LICENSE ] \
  && [ -f NOTICE ] \
  && runtime_source_diff codex-rs "$sync_dir/codex-rs" >/dev/null \
  && cmp -s LICENSE "$sync_dir/root/LICENSE" \
  && cmp -s NOTICE "$sync_dir/root/NOTICE"; then
  echo "Codex source already matches $YIJIE_CODEX_UPSTREAM_TAG ($YIJIE_CODEX_UPSTREAM_COMMIT)."
  exit 0
fi

if [ -n "$(git status --porcelain -- codex-rs LICENSE NOTICE)" ]; then
  echo "Refusing to materialize over local changes in codex-rs, LICENSE, or NOTICE." >&2
  exit 2
fi

previous_source="$sync_dir/previous-codex-rs"
if [ -d codex-rs ]; then
  mv codex-rs "$previous_source"
fi
mv "$sync_dir/codex-rs" codex-rs
cp "$sync_dir/root/LICENSE" LICENSE
cp "$sync_dir/root/NOTICE" NOTICE

echo "Materialized codex-rs from $YIJIE_CODEX_UPSTREAM_TAG ($YIJIE_CODEX_UPSTREAM_COMMIT)."
