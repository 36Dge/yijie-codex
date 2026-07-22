#!/usr/bin/env python3
"""Write a deterministic manifest for a built Runtime Baseline 0 artifact."""

import argparse
import json
import os
import subprocess
from pathlib import Path

from runtime_manifest import sha256_file, sha256_tree


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--schema-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--target", required=True)
    parser.add_argument("--upstream-url", required=True)
    parser.add_argument("--upstream-tag", required=True)
    parser.add_argument("--upstream-commit", required=True)
    parser.add_argument("--runtime-version", required=True)
    parser.add_argument("--rust-toolchain", required=True)
    parser.add_argument("--lock-normalization", required=True, type=Path)
    args = parser.parse_args()

    binary = args.binary.resolve()
    schema_dir = args.schema_dir.resolve()
    if not binary.is_file():
        raise SystemExit(f"Runtime binary is missing: {binary}")
    if not schema_dir.is_dir():
        raise SystemExit(f"Schema directory is missing: {schema_dir}")
    if not args.lock_normalization.is_file():
        raise SystemExit(f"Lock normalization report is missing: {args.lock_normalization}")

    reported_version = subprocess.run(
        [str(binary), "--version"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if args.runtime_version not in reported_version:
        raise SystemExit(
            f"Runtime version mismatch: expected {args.runtime_version}, got {reported_version}"
        )

    schema_files = sorted(path for path in schema_dir.rglob("*.json") if path.is_file())
    if not schema_files:
        raise SystemExit("Schema directory contains no JSON files")

    manifest = {
        "schemaVersion": 1,
        "baseline": "Runtime Baseline 0",
        "upstream": {
            "url": args.upstream_url,
            "tag": args.upstream_tag,
            "commit": args.upstream_commit,
        },
        "patches": [],
        "buildLock": json.loads(args.lock_normalization.read_text(encoding="utf-8")),
        "rustToolchain": args.rust_toolchain,
        "runtime": {
            "version": args.runtime_version,
            "reportedVersion": reported_version,
            "target": args.target,
            "binary": binary.name,
            "sizeBytes": os.path.getsize(binary),
            "sha256": sha256_file(binary),
        },
        "appServer": {
            "transport": "stdio",
            "experimentalApi": False,
            "schemaFileCount": len(schema_files),
            "schemaTreeSha256": sha256_tree(schema_dir),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(f"Wrote runtime manifest: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
