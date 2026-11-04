#!/usr/bin/env python3
"""Replay the approved model-declared public-message adapter candidate."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "canonical_native_public_source", Path(__file__).with_name("prepare-answer-completion.py")
)
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)

if __name__ == "__main__":
    source.main("write-native-public-messages-runtime-manifest.py")
