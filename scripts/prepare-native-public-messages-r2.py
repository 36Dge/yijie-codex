#!/usr/bin/env python3
"""Replay the reviewed single-message validation overlay after 0016."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "canonical_native_public_r2_source", Path(__file__).with_name("prepare-answer-completion.py")
)
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)

if __name__ == "__main__":
    source.main("write-native-public-messages-r2-runtime-manifest.py")
