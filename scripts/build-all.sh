#!/usr/bin/env bash
set -euo pipefail

if [ ! -f codex-rs/Cargo.toml ]; then
  echo "Codex source is not present; runtime build cannot run." >&2
  exit 2
fi

cargo build --manifest-path codex-rs/Cargo.toml --workspace --release
