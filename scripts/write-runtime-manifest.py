#!/usr/bin/env python3
"""Write a deterministic manifest for a patched Runtime Baseline 0 artifact."""

import argparse
import json
import os
import subprocess
from pathlib import Path

from runtime_manifest import sha256_file, sha256_tree


EXPECTED_PATCH_NAMES = (
    "0001-feat-126-filter-persistent-diagnostics.patch",
    "0002-feat-136-unified-exec-pre-emitter-command-lifecycle.patch",
    "0003-feat-137-stable-sandbox-provenance.patch",
    "0004-feat-137-deterministic-approval-producer.patch",
)


def reviewed_patch_files(patch_dir: Path, profile: str = "legacy") -> list[Path]:
    expected = EXPECTED_PATCH_NAMES
    if profile == "input-only":
        expected = EXPECTED_PATCH_NAMES[:2] + (
            "input-only/0003-input-only-execution.patch",
        )
        patch_files = [patch_dir / name for name in expected]
    else:
        patch_files = sorted(patch_dir.glob("*.patch"))
    patch_names = tuple(patch.relative_to(patch_dir).as_posix() for patch in patch_files)
    if patch_names != expected:
        raise SystemExit(
            "Runtime manifest requires the exact ordered FEAT-126/FEAT-136/FEAT-137 patch set: "
            f"expected={list(expected)!r}, got={list(patch_names)!r}"
        )
    if any(not patch.is_file() or patch.is_symlink() for patch in patch_files):
        raise SystemExit("Runtime manifest patch set contains a missing or unsafe patch")
    return patch_files


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
    parser.add_argument("--patch-dir", required=True, type=Path)
    parser.add_argument("--profile", choices=("legacy", "input-only"), default="legacy")
    args = parser.parse_args()

    binary = args.binary.resolve()
    schema_dir = args.schema_dir.resolve()
    if not binary.is_file():
        raise SystemExit(f"Runtime binary is missing: {binary}")
    if not schema_dir.is_dir():
        raise SystemExit(f"Schema directory is missing: {schema_dir}")
    if not args.lock_normalization.is_file():
        raise SystemExit(f"Lock normalization report is missing: {args.lock_normalization}")
    patch_files = reviewed_patch_files(args.patch_dir, args.profile)

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
        "patches": [
            {
                "path": f".yijie/patches/{patch.relative_to(args.patch_dir).as_posix()}",
                "sha256": sha256_file(patch),
            }
            for patch in patch_files
        ],
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
