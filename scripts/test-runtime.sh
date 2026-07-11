#!/usr/bin/env bash
set -euo pipefail

if [ ! -f codex-rs/Cargo.toml ]; then
  echo "Codex source is not present; runtime compatibility tests cannot run." >&2
  exit 2
fi

cargo test --manifest-path codex-rs/Cargo.toml --workspace
