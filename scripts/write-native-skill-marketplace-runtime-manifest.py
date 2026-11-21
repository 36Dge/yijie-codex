"""FEAT-174 native local marketplace policy, state and refresh adapters."""
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("native_skill_market_previous", Path(__file__).with_name("write-document-runtime-manifest.py"))
previous_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous_module)
base = previous_module.base
previous = base.reviewed_patch_files
def reviewed_patches(patch_dir, profile="input-only"):
    patches = [patch_dir / "chat-models" / name for name in (
        "0025-native-skill-marketplace.patch", "0026-deep-search-model-view.patch",
        "0027-scoped-search-progress.patch", "0028-public-message-publication.patch",
        "0029-resume-after-terminal-error.patch", "0030-declared-public-preview.patch",
    )]
    if any(not patch.is_file() or patch.is_symlink() for patch in patches):
        raise SystemExit("Reviewed local Runtime patch unavailable")
    return previous(patch_dir, profile) + patches
base.reviewed_patch_files = reviewed_patches
if __name__ == "__main__":
    raise SystemExit(base.main())
