"""Prepare FEAT-174 by replaying the retained canonical patch chain."""
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("prepare_native_skill_market", Path(__file__).with_name("prepare-answer-completion.py"))
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
source.WORK = source.ROOT / ".local/native-skills-market/workspace"
if __name__ == "__main__":
    source.main("write-native-skill-marketplace-runtime-manifest.py")
