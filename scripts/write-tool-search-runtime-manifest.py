"""Append the native tool search transport to the retained native tool candidate."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("tool_search_previous",Path(__file__).with_name("write-interaction-tools-runtime-manifest.py"))
previous_module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous_module)
base=previous_module.base
previous=base.reviewed_patch_files

def reviewed_patches(patch_dir,profile="input-only"):
    patch=patch_dir/"chat-models/0023-tool-search-function-transport.patch"
    if not patch.is_file() or patch.is_symlink():
        raise SystemExit("Reviewed tool search patch unavailable")
    return previous(patch_dir,profile)+[patch]

base.reviewed_patch_files=reviewed_patches
if __name__=="__main__":
    raise SystemExit(base.main())
