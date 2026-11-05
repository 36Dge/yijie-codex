#!/usr/bin/env python3
"""Replay the reviewed reviewed explicit spelling overlay after 0017."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "canonical_native_public_r3_source", Path(__file__).with_name("prepare-answer-completion.py")
)
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)

if __name__ == "__main__":
    source.main("write-native-public-messages-r3-runtime-manifest.py")
