#!/usr/bin/env python3
"""Reuse canonical source replay with the bounded plan-finalization extension."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "canonical_answer_source", Path(__file__).with_name("prepare-answer-completion.py")
)
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)

if __name__ == "__main__":
    source.main("write-execution-progress-runtime-manifest.py")
