#!/usr/bin/env python3
"""FEAT-164 r3 provenance; retain the immutable r2 generator and patch set."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "kimi_r2_manifest", Path(__file__).with_name("write-kimi-k31-pro-r2-runtime-manifest.py")
)
r2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r2)
base = r2.base
previous = base.reviewed_patch_files


def reviewed_patches(patch_dir, profile="input-only"):
    patches = previous(patch_dir, profile)
    patch = patch_dir / "chat-models/0009-feat-164-native-failure-terminals.patch"
    if not patch.is_file() or patch.is_symlink():
        raise SystemExit("FEAT-164 reviewed native terminal patch missing or unsafe")
    return patches + [patch]


base.reviewed_patch_files = reviewed_patches
if __name__ == "__main__":
    raise SystemExit(base.main())
