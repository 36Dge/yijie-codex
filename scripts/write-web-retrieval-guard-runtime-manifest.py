#!/usr/bin/env python3
"""Canonical execution-guard provenance, retaining the complete r5 patch chain."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "guard_previous_manifest", Path(__file__).with_name("write-kimi-k31-pro-r5-runtime-manifest.py")
)
previous_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous_module)
base = previous_module.base
previous = base.reviewed_patch_files


def reviewed_patches(patch_dir, profile="input-only"):
    patch = patch_dir / "chat-models/0012-web-retrieval-execution-guard.patch"
    if not patch.is_file() or patch.is_symlink():
        raise SystemExit("Reviewed execution guard patch unavailable")
    return previous(patch_dir, profile) + [patch]


base.reviewed_patch_files = reviewed_patches
if __name__ == "__main__":
    raise SystemExit(base.main())
