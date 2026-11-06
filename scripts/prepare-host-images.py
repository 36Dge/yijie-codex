"""Replay the full authorized image candidate in its own local build source root."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("prepare_candidate", Path(__file__).with_name("prepare-answer-completion.py"))
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
source.WORK = source.ROOT / ".local/host-images/workspace"
if __name__ == "__main__":
    source.main("write-host-image-runtime-manifest.py")
