#!/usr/bin/env python3
"""Canonical answer-completion provenance, retaining the complete r5 patch chain."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "answer_previous_manifest", Path(__file__).with_name("write-web-retrieval-guard-runtime-manifest.py")
)
previous_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous_module)
base = previous_module.base
previous = base.reviewed_patch_files


def reviewed_patches(patch_dir, profile="input-only"):
    patch = patch_dir / "chat-models/0013-answer-completion.patch"
    if not patch.is_file() or patch.is_symlink():
        raise SystemExit("Reviewed answer completion patch unavailable")
    return previous(patch_dir, profile) + [patch]


base.reviewed_patch_files = reviewed_patches
if __name__ == "__main__":
    raise SystemExit(base.main())
