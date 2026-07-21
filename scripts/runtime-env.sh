#!/usr/bin/env bash
set -euo pipefail

runtime_repo_root() {
  cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd
}

load_upstream_metadata() {
  local repo_root="$1"
  local metadata_file="$repo_root/.yijie/upstream.env"

  if [ ! -f "$metadata_file" ]; then
    echo "Missing upstream metadata: $metadata_file" >&2
    return 1
  fi

  # This file is committed repository metadata and contains no secrets.
  # shellcheck disable=SC1090
  source "$metadata_file"

  local required=(
    YIJIE_CODEX_UPSTREAM_URL
    YIJIE_CODEX_UPSTREAM_TAG
    YIJIE_CODEX_UPSTREAM_COMMIT
    YIJIE_CODEX_UPSTREAM_SUBTREE
    YIJIE_CODEX_RUNTIME_VERSION
    YIJIE_CODEX_RUST_TOOLCHAIN
    YIJIE_CODEX_PRIMARY_RELEASE_TARGET
  )
  local name
  for name in "${required[@]}"; do
    if [ -z "${!name:-}" ]; then
      echo "Missing required upstream metadata: $name" >&2
      return 1
    fi
  done

  if [[ ! "$YIJIE_CODEX_UPSTREAM_COMMIT" =~ ^[0-9a-f]{40}$ ]]; then
    echo "Upstream commit must be a full 40-character SHA." >&2
    return 1
  fi
  if [ "$YIJIE_CODEX_UPSTREAM_SUBTREE" != "codex-rs" ]; then
    echo "Runtime Baseline 0 only supports the codex-rs subtree." >&2
    return 1
  fi
}

runtime_host_target() {
  rustc -vV | sed -n 's/^host: //p'
}

runtime_platform_name() {
  local target="$1"
  case "$target" in
    *-apple-darwin) echo "macos" ;;
    *-linux-*) echo "linux" ;;
    *-windows-*|*-pc-windows-*) echo "windows" ;;
    *) echo "unknown" ;;
  esac
}

runtime_artifact_dir() {
  local repo_root="$1"
  local target="$2"
  local platform
  platform="$(runtime_platform_name "$target")"
  printf '%s/.yijie/build/%s/%s\n' "$repo_root" "$platform" "$target"
}

runtime_binary_path() {
  local repo_root="$1"
  local target="$2"
  local artifact_dir
  artifact_dir="$(runtime_artifact_dir "$repo_root" "$target")"
  case "$target" in
    *-windows-*|*-pc-windows-*) printf '%s/codex.exe\n' "$artifact_dir" ;;
    *) printf '%s/codex\n' "$artifact_dir" ;;
  esac
}
