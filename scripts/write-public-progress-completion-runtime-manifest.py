#!/usr/bin/env python3
"""Retain native continuation and the bounded finalizer; extend only its classifier."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "public_progress_previous_manifest", Path(__file__).with_name("write-execution-progress-runtime-manifest.py")
)
previous_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous_module)
base = previous_module.base
previous = base.reviewed_patch_files


def reviewed_patches(patch_dir, profile="input-only"):
    patch = patch_dir / "chat-models/0015-public-progress-completion.patch"
    if not patch.is_file() or patch.is_symlink():
        raise SystemExit("Reviewed public progress completion patch unavailable")
    return previous(patch_dir, profile) + [patch]


base.reviewed_patch_files = reviewed_patches
if __name__ == "__main__":
    raise SystemExit(base.main())
