"""FEAT-174 native local marketplace policy, state and refresh adapters."""
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("native_skill_market_previous", Path(__file__).with_name("write-document-runtime-manifest.py"))
previous_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous_module)
base = previous_module.base
previous = base.reviewed_patch_files
def reviewed_patches(patch_dir, profile="input-only"):
    patch = patch_dir / "chat-models/0025-native-skill-marketplace.patch"
    if not patch.is_file() or patch.is_symlink():
        raise SystemExit("Native skill marketplace patch unavailable")
    return previous(patch_dir, profile) + [patch]
base.reviewed_patch_files = reviewed_patches
if __name__ == "__main__":
    raise SystemExit(base.main())
