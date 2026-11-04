#!/usr/bin/env python3
"""Extend the reviewed chain; native rollout_budget remains unchanged."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "progress_previous_manifest", Path(__file__).with_name("write-answer-completion-runtime-manifest.py")
)
previous_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous_module)
base = previous_module.base
previous = base.reviewed_patch_files


def reviewed_patches(patch_dir, profile="input-only"):
    patch = patch_dir / "chat-models/0014-execution-progress.patch"
    if not patch.is_file() or patch.is_symlink():
        raise SystemExit("Reviewed execution progress patch unavailable")
    return previous(patch_dir, profile) + [patch]


base.reviewed_patch_files = reviewed_patches
if __name__ == "__main__":
    raise SystemExit(base.main())
