#!/usr/bin/env python3
"""FEAT-156 manifest profile; preserve the committed input-only generator."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "input_only_manifest", Path(__file__).with_name("write-runtime-manifest.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
input_only_patches = module.reviewed_patch_files


def reviewed_patches(patch_dir, profile="input-only"):
    if profile != "input-only":
        raise SystemExit("FEAT-156 requires the input-only base profile")
    patches = input_only_patches(patch_dir, profile)
    patch = patch_dir / "chat-models/0004-feat-156-upstream-tool-choice.patch"
    if not patch.is_file() or patch.is_symlink():
        raise SystemExit("FEAT-156 patch missing or unsafe")
    stream_patch = patch_dir / "chat-models/0005-feat-156-terminal-tool-arguments.patch"
    if not stream_patch.is_file() or stream_patch.is_symlink():
        raise SystemExit("FEAT-156 stream patch missing or unsafe")
    return patches + [patch, stream_patch]


module.reviewed_patch_files = reviewed_patches
if __name__ == "__main__":
    raise SystemExit(module.main())
