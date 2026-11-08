"""Compose the native tool integration from the retained Host image candidate."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "native_tools_previous_manifest", Path(__file__).with_name("write-host-image-runtime-manifest.py")
)
previous_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous_module)
base = previous_module.base
previous = base.reviewed_patch_files


def reviewed_patches(patch_dir, profile="input-only"):
    patches = [patch_dir / "chat-models" / name for name in [
        "0020-native-tool-integration.patch", "0021-native-tool-policy-audit.patch"
    ]]
    if any(not patch.is_file() or patch.is_symlink() for patch in patches):
        raise SystemExit("Reviewed native tool integration patch unavailable")
    return previous(patch_dir, profile) + patches


base.reviewed_patch_files = reviewed_patches
if __name__ == "__main__":
    raise SystemExit(base.main())
