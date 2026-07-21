#!/usr/bin/env python3
"""Allow only release-version normalization for local workspace packages."""

import argparse
import copy
import hashlib
import json
import tomllib
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-lock", required=True, type=Path)
    parser.add_argument("--resolved-lock", required=True, type=Path)
    parser.add_argument("--runtime-version", required=True)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    upstream = tomllib.loads(args.upstream_lock.read_text(encoding="utf-8"))
    resolved = tomllib.loads(args.resolved_lock.read_text(encoding="utf-8"))
    normalized = copy.deepcopy(resolved)

    normalized_packages = []
    for package in normalized.get("package", []):
        if "source" not in package and package.get("version") == args.runtime_version:
            normalized_packages.append(package.get("name", "<unnamed>"))
            package["version"] = "0.0.0"

    if normalized != upstream:
        raise SystemExit(
            "Cargo.lock drift is broader than local workspace release-version normalization"
        )
    if not normalized_packages:
        raise SystemExit("Cargo.lock normalization changed no local workspace packages")

    report = {
        "schemaVersion": 1,
        "policy": "local-workspace-version-normalization-only",
        "fromVersion": "0.0.0",
        "toVersion": args.runtime_version,
        "normalizedPackageCount": len(normalized_packages),
        "upstreamLockSha256": sha256(args.upstream_lock),
        "resolvedLockSha256": sha256(args.resolved_lock),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.report.with_suffix(args.report.suffix + ".tmp")
    temporary.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(args.report)
    print(
        f"Verified release lock normalization for {len(normalized_packages)} local workspace packages."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
