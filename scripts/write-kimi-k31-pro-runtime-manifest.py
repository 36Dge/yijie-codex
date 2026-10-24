#!/usr/bin/env python3
"""FEAT-164 candidate identity, preserving all prior manifest generators."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "web_sources_manifest", Path(__file__).with_name("write-web-search-sources-runtime-manifest.py")
)
web = importlib.util.module_from_spec(spec)
spec.loader.exec_module(web)
base = web.module.module
previous = base.reviewed_patch_files


def reviewed_patches(patch_dir, profile="input-only"):
    patches = previous(patch_dir, profile)
    patch = patch_dir / "chat-models/0007-feat-164-kimi-k31-pro.patch"
    if not patch.is_file() or patch.is_symlink():
        raise SystemExit("FEAT-164 reviewed model migration patch missing or unsafe")
    return patches + [patch]


base.reviewed_patch_files = reviewed_patches
if __name__ == "__main__":
    raise SystemExit(base.main())
