#!/usr/bin/env python3
"""FEAT-164 r5 provenance; retain the immutable r4 generator and patch set."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "kimi_r4_manifest", Path(__file__).with_name("write-kimi-k31-pro-r4-runtime-manifest.py")
)
r4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r4)
base = r4.base
previous = base.reviewed_patch_files


def reviewed_patches(patch_dir, profile="input-only"):
    patches = previous(patch_dir, profile)
    patch = patch_dir / "chat-models/0011-feat-164-graceful-state-close.patch"
    if not patch.is_file() or patch.is_symlink():
        raise SystemExit("FEAT-164 reviewed normal state shutdown patch missing or unsafe")
    return patches + [patch]


base.reviewed_patch_files = reviewed_patches
if __name__ == "__main__":
    raise SystemExit(base.main())
