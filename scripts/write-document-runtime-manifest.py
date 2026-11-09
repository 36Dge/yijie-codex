"""FEAT-171 cooperative native shutdown on the retained tool-search chain."""
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("document_previous",Path(__file__).with_name("write-tool-search-runtime-manifest.py"))
previous_module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous_module)
base=previous_module.base
previous=base.reviewed_patch_files
def reviewed_patches(patch_dir,profile="input-only"):
    patch=patch_dir/"chat-models/0024-cooperative-exec-shutdown.patch"
    if not patch.is_file() or patch.is_symlink():
        raise SystemExit("Reviewed cooperative shutdown patch unavailable")
    return previous(patch_dir,profile)+[patch]
base.reviewed_patch_files=reviewed_patches
if __name__=="__main__":
    raise SystemExit(base.main())
