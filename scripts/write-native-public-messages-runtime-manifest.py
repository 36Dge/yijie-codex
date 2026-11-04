#!/usr/bin/env python3
"""Preserve the prior chain; add the owner-approved native message adapter."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "native_public_previous_manifest",
    Path(__file__).with_name("write-public-progress-completion-runtime-manifest.py"),
)
previous_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous_module)
base = previous_module.base
previous = base.reviewed_patch_files


def reviewed_patches(patch_dir, profile="input-only"):
    patch = patch_dir / "chat-models/0016-native-public-messages.patch"
    if not patch.is_file() or patch.is_symlink():
        raise SystemExit("Reviewed native public-message patch unavailable")
    return previous(patch_dir, profile) + [patch]


base.reviewed_patch_files = reviewed_patches
if __name__ == "__main__":
    raise SystemExit(base.main())
