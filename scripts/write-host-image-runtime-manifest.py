"""Compose the FEAT-168 candidate from the fixed native-public-messages-r3 chain."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("image_predecessor", Path(__file__).with_name("write-native-public-messages-r3-runtime-manifest.py"))
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
base = prior.base
before_images = base.reviewed_patch_files


def reviewed_patches(patch_dir, profile="input-only"):
    patch = patch_dir / "chat-models/0019-host-image-generation.patch"
    if not patch.is_file() or patch.is_symlink():
        raise SystemExit("Missing reviewed Host image patch")
    return before_images(patch_dir, profile) + [patch]


base.reviewed_patch_files = reviewed_patches
if __name__ == "__main__":
    raise SystemExit(base.main())
