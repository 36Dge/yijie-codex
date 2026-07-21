#!/usr/bin/env python3
"""Canonicalize generated JSON files without changing their data model."""

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True, type=Path)
    args = parser.parse_args()

    paths = sorted(path for path in args.directory.rglob("*.json") if path.is_file())
    if not paths:
        raise SystemExit(f"No JSON files found under {args.directory}")

    for path in paths:
        value = json.loads(path.read_text(encoding="utf-8"))
        path.write_text(
            json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    print(f"Canonicalized {len(paths)} JSON files under {args.directory}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
