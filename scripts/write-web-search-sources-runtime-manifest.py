#!/usr/bin/env python3
"""Source metadata candidate; reuse the existing manifest and patch identity rules."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "stream_manifest", Path(__file__).with_name("write-chat-model-stream-runtime-manifest.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
previous = module.module.reviewed_patch_files


def reviewed_patches(patch_dir, profile="input-only"):
    patches = previous(patch_dir, profile)
    patch = patch_dir / "chat-models/0006-native-web-search-sources.patch"
    if not patch.is_file() or patch.is_symlink():
        raise SystemExit("Web search sources patch missing or unsafe")
    return patches + [patch]


module.module.reviewed_patch_files = reviewed_patches
if __name__ == "__main__":
    raise SystemExit(module.module.main())
