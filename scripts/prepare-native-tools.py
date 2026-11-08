"""Materialize the canonical native tools candidate without changing prior sources."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "prepare_native_tools", Path(__file__).with_name("prepare-answer-completion.py")
)
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
source.WORK = source.ROOT / ".local/native-tools/workspace"
if __name__ == "__main__":
    source.main("write-native-tools-runtime-manifest.py")
