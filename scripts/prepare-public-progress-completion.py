#!/usr/bin/env python3
"""Replay the existing completion chain with the approved writing-preamble fix."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "canonical_public_progress_source", Path(__file__).with_name("prepare-answer-completion.py")
)
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)

if __name__ == "__main__":
    source.main("write-public-progress-completion-runtime-manifest.py")
